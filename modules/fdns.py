import subprocess
import modules.utils
from more_itertools import unique_everseen


# Converts subdomain text in order to be parsed by grep and jq commands
# It is important to keep the same domains order in both 'grep_list' and 'jq_regex_list'

def _grep_jq_convert(domain):
    '''Transforms a (sub)domain into two strings: intended for 'grep' and 'jq' subprocess, respectively.
    
    Example:
    domain input: 'example.com'
    
    output: '.example.com' (for grep)
            '\\.example\\.com' (for jq)'''
    

    domain = domain.strip()
    sliced_domain = domain.split('.')

    grep_str = '.'       
    jq_str = '\\\\.'
    i = 1
    for item in sliced_domain:
        grep_str += item
        jq_str += item
        if i < len(sliced_domain):
            grep_str += '.'
            jq_str += '\\\\.'
            i += 1

    return grep_str, jq_str


def grep_subd_fdns(domain, fdns_file):
    '''Parses for a domain in a 'Rapid7 Open Data FDNS' database file and returns a list of subdomains.
    
    Database files available at https://opendata.rapid7.com'''
    
    #! Dev Warning 0: 'shell=True' was needed to avoid mem kill, 
        # as opposed to using multiple 'p = subprocess.run' and 'input=p.stdout' method
    
    #! Dev Warning 1: this step may heavily load the CPU. TODO try multithreading in the future'

    fdns_outp_list = []
    grep_str, jq_str = _grep_jq_convert(domain)

    jq_filter = f'\'if (.name | test("{jq_str}")) then .name elif (.value | test("{jq_str}")) then .value else empty end\''

    p = subprocess.run([f'zcat {fdns_file}\
        | grep -F {grep_str}\
        | jq -crM {jq_filter}\
        | sort\
        | uniq\
        '], capture_output=True, shell=True, text=True)

    fdns_outp_list.extend(p.stdout.split('\n'))

    #!TODO BEGIN DEL TEST
    for item in fdns_outp_list:
        print(item)
    #!TODO END DEL TEST

    # Removing eventual duplicated results
    fdns_outp_list = list(unique_everseen(fdns_outp_list))
    
    # Removing eventual empty results
    if '' in fdns_outp_list:
        fdns_outp_list.remove('')

    #!TODO BEGIN DEL TEST
    from datetime import datetime
    base_dir = f'/tmp/'
    ftimestamp = datetime.now().strftime('%y%m%d-%H%M%S')
    test_file = f'{base_dir}{ftimestamp}-test_grep_subd_fdns-fdns_outp_list-append_list{domain}'
    with open(test_file, 'a') as f:
        for item in fdns_outp_list:
            f.write(item + '\n')
    #!TODO END DEL TEST
    return fdns_outp_list
