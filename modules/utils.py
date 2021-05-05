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
    merged_list.extend(list(unique_everseen(list1)))

    merged_list.extend(list(unique_everseen(list2)))

    if args:
        for arg in args:
            merged_list.extend(list(unique_everseen(arg)))
    
    return merged_list


def count_new_unique(main_list, new_list):
    '''Returns an integer count of unique elements not contained in main list'''

    return len(set(new_list) - set(main_list))


def count_lines(file_path):
    line_count = 0
    with open(file_path, 'r') as f:
        for line in f:
            line_count += 1


def write_full_output(file_path, string_output):
    with open(file_path, 'w') as f:
        f.write(str(string_output))


def write_list(file_path, string_output):
    with open(file_path, 'w') as f:
        f.write(string_output)


def append_full_output(file_path, string_output):
    with open(file_path, 'a') as f:
        for line in string_output.split('\n'):
            f.write(line + '\n')


def append_list(file_path, list_output):
    with open(file_path, 'a') as f:
        for item in list_output:
            f.write(item + '\n')


def get_ndjson_jq(file_path):
    p = subprocess.run([f'grep NOERROR {NDJ_OUTP_1}\
    | jq -crM \'.data | .answers | .[] | .name\'\
    | sort\
    | uniq'],
        shell=True, capture_output=True, text=True)


def get_jq(jq_filter, file_path):
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
    
    results_l = []

    results_l.extend(p.split('\\n'))
    results_l.remove('') # remove any empty element left on list

    return results_l
