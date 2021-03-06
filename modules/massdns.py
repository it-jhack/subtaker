import json
import ndjson
import os
import subprocess
import modules.utils


def get_massdns(subdomains_l, resolvers_f, concurrent_n):
    
    massdns_cmd = [
        os.environ['massdns'],
        '-s', str(concurrent_n),
        '-t', 'A',
        '-o', 'J',
        '-r', resolvers_f,
        '--flush'
    ]

    processed = []
    
    for line in modules.utils.exec_and_readlines(massdns_cmd, subdomains_l):
        if not line:
            continue
        processed.append(json.loads(line.strip()))
    
    return processed


def massdns_dump(subdomains_l, resolvers_f, concurrent_n, output_f):
    with open(output_f, 'a') as f:
        ndjson.dump(get_massdns(subdomains_l, resolvers_f, concurrent_n), f)


def grep_subds_ndjson(file_path):

    #! Dev Warning 0: If mem kill is an issue on low-end systems, blend all
        # 'p = subprocess.run' and 'input=p.stdout' into a single 'shell=True' cmd,
        # as did previously on 'fdns.py' file on 'def grep_subds_fdns(domains_list, fdns_file):'

    jq_filter = '.data | .answers | .[] | .name'

    # Reusing the same 'p' var to save memory on large outputs
    p = subprocess.run(['grep', 'NOERROR', file_path], capture_output=True)

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

    p = str(p.stdout).strip('b\'')

    results_list = []
    results_list.extend(p.split('\\n'))

    # Remove any empty element left on list
    if '' in results_list:
        results_list.remove('') 

    # Each item in results_list finishes with '.' char;
    
    # You may or may not want to remove that char,
        # depending on what you'll do with the list
    
    return results_list
