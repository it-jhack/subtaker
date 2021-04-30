
import subprocess


# Converts subdomain text in order to be parsed by grep and jq commands
# It is important to keep the same domains order in both 'grep_list' and 'jq_regex_list'

def subdomain_convert(domains_list):
    grep_list = []
    jq_regex_list = []

    for domain in domains_list:
        domain = domain.strip()
        sliced_domain = domain.split('.')

        grep_str = '.'       
        jq_regex_str = '\\\\.'
        i = 1
        for item in sliced_scope:
            grep_str += item
            jq_regex_str += item
            if i < len(sliced_scope):
                grep_str += '.'
                jq_regex_str += '\\\\.'
                i += 1
        grep_list.append(grep_str)
        jq_regex_list.append(jq_regex_str)

    return grep_list, jq_regex_list


def grep_fdns(domains_list, fdns_file):
    fdns_outp_list = []
    grep_list, jq_regex_list = subdomain_convert(domains_list)
    
    for grep_item, jq_item in zip(grep_list, jq_regex_list):

        p = subprocess.run([f'zcat {fdns_file}\
        | grep -F \'{grep_item}\'\
        | jq -crM \'if (.name | test("{jq_item}")) then .name elif (.value | test("{jq_item}")) then .value else empty end\'\
        | sort\
        | uniq'],
            shell=True, capture_output=True, text=True)
                # grep -F = fixed strings (not regex)
                # jq -c = compact instead of pretty-printed output; 
                # -r = output raw strings, not JSON texts; 
                # -M = monochrome (don't colorize JSON);

        fdns_outp_list.extend(p.stdout.split('\n'))

    # Removing duplicated results
    fdns_outp_list = list(unique_everseen(fdns_outp_list))
    
    # Removing empty results
    if '' in fdns_outp_list:
        fdns_outp_list.remove('')

    return fdns_outp_list
