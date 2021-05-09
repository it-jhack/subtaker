 
import modules.utils
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
    output_list = []
    for line in modules.utils.exec_and_readlines(amass_cmd, domain):
        if not line:
            continue
        output_list.append(line)
    
    # Removing domain repetitions
    output_list = list(unique_everseen(output_list))

    # Removing empty element from list
    if '' in output_list:
        output_list.remove('')

    return output_list
