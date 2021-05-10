
import subprocess
import modules.utils
from more_itertools import unique_everseen


# Converts subdomain text in order to be parsed by grep and jq commands
# It is important to keep the same domains order in both 'grep_list' and 'jq_regex_list'

def _grep_jq_convert(domains_list):
    '''Transforms a list of items into two lists: intended for 'grep' and 'jq' subprocess, respectively.
    Be careful to parse both lists at the same order, such as by using the commands:

    grep_list, jq_regex_list = _grep_jq_convert(domains_list)
    
    for grep_item, jq_item in zip(grep_list, jq_regex_list):'''

    grep_list = []
    jq_regex_list = []

    for domain in domains_list:
        domain = domain.strip()
        sliced_domain = domain.split('.')

        grep_str = '.'       
        jq_regex_str = '\\\\.'
        i = 1
        for item in sliced_domain:
            grep_str += item
            jq_regex_str += item
            if i < len(sliced_domain):
                grep_str += '.'
                jq_regex_str += '\\\\.'
                i += 1
        grep_list.append(grep_str)
        jq_regex_list.append(jq_regex_str)

    return grep_list, jq_regex_list


def grep_subds_fdns(domains_list, fdns_file):
    '''Parses a 'Rapid7 Open Data FDNS' database file and returns a list of subdomains.
    
    See more at https://opendata.rapid7.com'''
    
    #! Dev Warning 0: 'shell=True' was needed to avoid mem kill, 
        # as opposed to using multiple 'p = subprocess.run' and 'input=p.stdout' method
    
    #! Dev Warning 1: this step may heavily load the CPU. TODO try multithreading in the future'

    fdns_outp_list = []
    grep_list, jq_regex_list = _grep_jq_convert(domains_list)

    #!TODO BEGIN DEL TEST
    print('\n> testing if list items/order is correct:\n')
    for item in grep_list: #test if list items/order is correct
        print(item)
    print()
    for item in jq_regex_list:
        print(item)
    print()
    for grep_item, jq_item in zip(grep_list, jq_regex_list):
        print(grep_item + ', ' + jq_item)
    print()
    from datetime import datetime
    base_dir = f'/tmp/'
    ftimestamp = datetime.now().strftime('%y%m%d-%H%M%S')
    test_file = f'{base_dir}{ftimestamp}-test_grep_subds_fdns-zip_grep_and_jq_items-append_lists'
    #!TODO END DEL TEST
    
    for grep_item, jq_item in zip(grep_list, jq_regex_list):
        #!TODO BEGIN DEL TEST
        with open(test_file, 'a') as f:
            f.write(grep_item + ',' + jq_item + '\n')
        #!TODO END DEL TEST


        jq_filter = f'\'if (.name | test("{jq_item}")) then .name elif (.value | test("{jq_item}")) then .value else empty end\''

        p = subprocess.run([f'zcat {fdns_file}\
            | grep -F {grep_item}\
            | jq -crM {jq_filter}\
            | sort\
            | uniq\
            '], capture_output=True, shell=True, text=True)

        fdns_outp_list.extend(p.stdout.split('\n'))

        #!TODO BEGIN DEL TEST
        for item in fdns_outp_list:
            print(item)
        #!TODO END DEL TEST

    # Removing duplicated results
    fdns_outp_list = list(unique_everseen(fdns_outp_list))
    
    # Removing empty results
    if '' in fdns_outp_list:
        fdns_outp_list.remove('')

    #!TODO BEGIN DEL TEST
    from datetime import datetime
    base_dir = f'/tmp/'
    ftimestamp = datetime.now().strftime('%y%m%d-%H%M%S')
    test_file = f'{base_dir}{ftimestamp}-test_grep_subds_fdns-fdns_outp_list-append_list'
    with open(test_file, 'a') as f:
        for item in fdns_outp_list:
            f.write(item + '\n')
    #!TODO END DEL TEST
    return fdns_outp_list
