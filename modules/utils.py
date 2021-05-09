from datetime import datetime
from more_itertools import unique_everseen
import subprocess


def get_time_hhmm():
    '''hh:mm format is helpful to print human-readable time'''
    return datetime.now().strftime('%H:%M')


def get_time_yymmdd_hhmm():
    '''\'yymmdd-hhmm format is helpful to orderly name files.
    \'Seconds\' are omitted to improve human readability.'''
    
    return datetime.now().strftime('%y%m%d-%H%M')


def get_time_yymmdd_hhmmss():
    '''\'yymmdd-hhmmss format is helpful to orderly name different files that might be created within the minute'''
    
    return datetime.now().strftime('%y%m%d-%H%M%S')


def screen_msg(message):
    '''Helpful to print events while running the program'''
    print(f'{get_time_hhmm()} > {message}')


def merge_lists(list1, list2, *args):
    '''Merges two or more lists and deletes redundant elements, returning a new list.
    The lists passed as arguments are not affected.'''

    # Removing duplicates at every 'extend()' to prevent 'out of memory' process kill 
        # on humongous lists
    
    # unique_everseen() = Find unique elements, preserving their order. Remembers 
        # all elements ever seen.

    merged_list = []
    # Extending already unique items to prevent large lists from
        # killing process due to lack of memory.
    merged_list.extend(list(unique_everseen(list1)))

    merged_list.extend(list(unique_everseen(list2)))

    if args:
        for arg in args:
            merged_list.extend(list(unique_everseen(arg)))
    
    # Remove possible duplicates resulted from intersection between lists
    merged_list = list(unique_everseen(merged_list))

    return merged_list


def exec_and_readlines(cmd, domains):
    '''Executes a command, having a (sub)domains list as argument'''

    domains_str = bytes('\n'.join(domains), 'ascii')
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)
    stdout, stderr = proc.communicate(input=domains_str)

    return [j.decode('utf-8').strip() for j in stdout.splitlines() if j != b'\n']


def append_list_file(list, file):
    '''Append items from a list to the end of a file in separate lines. If file does not exist, it is created.'''
    with open(file, 'a') as f:
        for item in list:
            f.write(item + '\n')


def count_new_unique(main_list, new_list):
    '''Returns an integer count of unique elements not contained in main list'''

    return len(set(new_list) - set(main_list))


def count_lines(file_path):
    '''Returns how many lines there are in a given file.
    It is assumed that the last line is blank, so not included in the count.'''

    line_count = 0
    with open(file_path, 'r') as f:
        for line in f:
            line_count += 1

    return line_count
