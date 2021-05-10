import json
import ndjson
import os
import subprocess
import modules.utils


#!TODO BEGIN DEL IF utils.exec_and_readlines
# def _exec_and_readlines(cmd, domains):
#     '''Executes a command, having a (sub)domains list as argument'''

#     domains_str = bytes('\n'.join(domains), 'ascii')
#     proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)
#     stdout, stderr = proc.communicate(input=domains_str)

#     return [j.decode('utf-8').strip() for j in stdout.splitlines() if j != b'\n']
#!TODO END DEL IF utils.exec_and_readlines


def get_massdns(subdomains_l, resolvers_f, concurrent_n):
    
    massdns_cmd = [
        os.environ['massdns'],
        '-s', str(concurrent_n),
        '-t', 'A',
        '-o', 'J',
        '-r', resolvers_f,
        '--flush'
    ]
    # -s: Number of concurrent lookups. (Default: 10000)
    # -t: Record type to be resolved. (Default: A)
    # -o: Flags for output formatting:
        # S - simple text output
        # F - full text output
        # B - binary output
        # J - ndjson output
    # -r: Text file containing DNS resolvers.
    # --flush: Forces the data to be written out whenever a response is received.

    processed = []
    # for line in _exec_and_readlines(massdns_cmd, subdomains_l): #!TODO BEGIN DEL THIS LINE
    for line in modules.utils.exec_and_readlines(massdns_cmd, subdomains_l): #!TODO END DEL OR THIS LINE
        if not line:
            continue
        processed.append(json.loads(line.strip()))
    
    #!TODO BEGIN DEL TEST
    from datetime import datetime
    base_dir = f'/tmp/'
    ftimestamp = datetime.now().strftime('%y%m%d-%H%M%S')
    test_file = f'{base_dir}{ftimestamp}-test_get_massdns-processed-write'
    with open(test_file, 'w') as f:
        for item in processed:
            f.write(str(item) + '\n')
    #!TODO END DEL TEST
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
    #!TODO BEGIN DEL TEST
    from datetime import datetime
    base_dir = f'/tmp/'
    ftimestamp = datetime.now().strftime('%y%m%d-%H%M%S')
    test_file = f'{base_dir}{ftimestamp}-test_massdns-grep_subds_ndjson-results_list-append_item'
    with open(test_file, 'a') as f:
        for item in results_list:
                f.write(item + '\n')
    #!TODO END DEL TEST
    return results_list
