import json
import ndjson
import os
import subprocess


def _exec_and_readlines(cmd, domains):
    '''Executes a command, having a list of domains or subdomains as argument'''

    domains_str = bytes('\n'.join(domains), 'ascii')
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)
    stdout, stderr = proc.communicate(input=domains_str)

    return [j.decode('utf-8').strip() for j in stdout.splitlines() if j != b'\n']


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
    for line in _exec_and_readlines(massdns_cmd, subdomains_l):
        if not line:
            continue
        processed.append(json.loads(line.strip()))
    
    return processed


def massdns_dump(subdomains_l, resolvers_f, concurrent_n, output_f):
    with open(output_f, 'a') as f:
        ndjson.dump(get_massdns(subdomains_l, resolvers_f, concurrent_n), f)
