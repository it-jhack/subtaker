from datetime import datetime
from more_itertools import unique_everseen

def get_time_hhmm():
    return datetime.now().strftime('%H:%M')

def get_time_yymmdd_hhmm():
    return datetime.now().strftime('%y%m%d-%H%M')

def screen_msg(message):
    print(f'{get_time_hhmm()} > {message}')

def exec_and_readlines(cmd, domains):
    domains_str = bytes('\n'.join(domains), 'ascii')
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)
    stdout, stderr = proc.communicate(input=domains_str)

    return [j.decode('utf-8').strip() for j in stdout.splitlines() if j != b'\n']

# Merge 2 or more lists, remove duplicates
def merge_lists(main_list, *args):
    
    for arg in args:
        main_list.extend(arg)
        main_list = list(unique_everseen(main_list))
    
    return main_list

# Merge 2 lists, remove duplicates, count how many added new elements
def merge_and_count_new_unique(main_list, new_list):
    old_main_len = len(main_list)
    main_list = merge_lists(main_list, new_list)

    return main_list, len(main_list) - old_main_len
