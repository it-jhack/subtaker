import utils

def get_massdns(domains_list, resolvers_f, concurrent_n):
    massdns_cmd = [
        f'massdns',
        '-s', concurrent_n,
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
    for line in utils.exec_and_readlines(massdns_cmd, domains):
        if not line:
            continue
        processed.append(json.loads(line.strip()))
    
    return processed
