 
import utils
import subprocess
from more_itertools import unique_everseen

# Use Amass to get passive data

def run_amass_enum(domain):
    amass_cmd = [
        'amass', 
        'enum',
        '--passive',
        '-d', domain
    ]
    output = []
    for line in utils.exec_and_readlines(amass_cmd, domain):
        if not line:
            continue
        processed.append(line)
    
    # Removing domain repetitions
    output = list(unique_everseen(output))

    # Removing empty element from list
    if '' in output:
        output.remove('')

    return output
