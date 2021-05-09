
import subprocess
import modules.utils


# Converts subdomain text in order to be parsed by grep and jq commands
# It is important to keep the same domains order in both 'grep_list' and 'jq_regex_list'

def _subdomain_convert(domains_list):
    '''Transforms a list of items into two lists: intended for 'grep' and 'jq' subprocess, respectively.
    Be careful to parse both lists at the same order, such as by using the commands:

    grep_list, jq_regex_list = _subdomain_convert(domains_list)
    
    for grep_item, jq_item in zip(grep_list, jq_regex_list):'''

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


def grep_subds_fdns(domains_list, fdns_file):
    '''Parses a 'Rapid7 Open Data FDNS' database file and returns a list of subdomains.
    
    See more at https://opendata.rapid7.com'''

    fdns_outp_list = []
    grep_list, jq_regex_list = _subdomain_convert(domains_list)
    
    for grep_item, jq_item in zip(grep_list, jq_regex_list):

        p = subprocess.run(['zcat', fdns_file], capture_output=True)
        p = subprocess.run(['grep', '-F', grep_item], capture_output=True, input=p.stdout)

        # Filter checks if subdomain is on 'name' or 'value' field within FDNS file
        jq_filter = f'if (.name | test("{jq_item}")) then .name elif (.value | test("{jq_item}")) then .value else empty end'

        p = subprocess.run([
            'jq', '-crM', jq_filter
                # Returns 'bytes' type
                # -c: compact instead of pretty-printed output;
                # -r: output raw strings, not JSON texts;
                # -M: monochrome (don't colorize JSON);
        ],
        capture_output=True, input=p.stdout)

        p = subprocess.run(['sort'], capture_output=True, input=p.stdout)
        p = subprocess.run(['uniq'], capture_output=True, input=p.stdout)

        fdns_outp_list.extend(p.stdout.split('\n'))

    # Removing duplicated results
    fdns_outp_list = list(unique_everseen(fdns_outp_list))
    
    # Removing empty results
    if '' in fdns_outp_list:
        fdns_outp_list.remove('')

    return fdns_outp_list
