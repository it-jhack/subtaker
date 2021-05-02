from datetime import datetime
from more_itertools import unique_everseen


def get_time_hhmm():
    '''hh:mm format is helpful to print human-readable time'''
    return datetime.now().strftime('%H:%M')


def get_time_yymmdd_hhmm():
    '''\'yymmdd-hhmm format is helpful to orderly name files.
    \'Seconds\' are omitted to improve human readability.'''
    
    return datetime.now().strftime('%y%m%d-%H%M')


def screen_msg(message):
    '''Helpful to print events while running the program'''
    print(f'{get_time_hhmm()} > {message}')


def exec_and_readlines(cmd, domains):
    '''Executes a command, having a list of domains or subdomains as argument'''

    domains_str = bytes('\n'.join(domains), 'ascii')
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)
    stdout, stderr = proc.communicate(input=domains_str)

    return [j.decode('utf-8').strip() for j in stdout.splitlines() if j != b'\n']


def merge_lists(list1, list2, *args):
    '''Merges two or more lists and deletes redundant elements, returning a new list.
    The lists passed as arguments are not affected.'''

    # Removing duplicates at every 'extend()' to prevent 'out of memory' process kill 
        # on humongous lists
    
    # unique_everseen() = Find unique elements, preserving their order. Remembers 
        # all elements ever seen.

    merged_list = []
    merged_list.extend(list1)
    merged_list = list(unique_everseen(merged_list))

    merged_list.extend(list2)
    merged_list = list(unique_everseen(merged_list))

    if args:
        for arg in args:
            merged_list.extend(arg)
            merged_list = list(unique_everseen(merged_list))
    
    return merged_list


def count_new_unique(main_list, new_list):
    '''Returns an integer count of unique elements not contained in main list'''

    return len(set(new_list) - set(main_list))
