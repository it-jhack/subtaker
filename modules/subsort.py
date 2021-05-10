
# You can see this module's original repo at:
# https://github.com/it-jhack/subsort/

# This program removes subdomain redundancies and returns an optimized list.
# It saves A LOT of time when parsing large subdomain/dns files with grep.

''' EXAMPLE: 
Suppose you have a 30 GB .txt file full of DNS entries.
if you grep for the lines containing the domain "example.com"
you don't need to parse for "sub.example.com" as the results 
of the latter will be contained in the results of the former.
This program removes the subdomain redundancies, returning an
optimized list, which can later be used at a parsing cmd tool
such as grep.
'''


def subds_occurrence_logic_check(subds_list):
    sorted_subds_list = sorted(subds_list, key=len)
    subds_list_range = len(sorted_subds_list)

    # main list to add unique subdomains.
    optimized_list = [] 

    for i in range(subds_list_range):
        
        # temporary list
        temp_list = []
        temp_list.extend(sorted_subds_list)
        temp_list.remove(sorted_subds_list[i])
        temp_list_string = str(temp_list)

        # main logic is on if-else
        if sorted_subds_list[i] in temp_list_string:
            flag = 0
            for item in optimized_list:
                if item in sorted_subds_list[i]:
                    flag += 1
            if flag == 0:
                optimized_list.append(sorted_subds_list[i])
        else:
            temp_list_string_2 = str(optimized_list)
            if sorted_subds_list[i] not in temp_list_string_2:
                flag = 0
                for item in optimized_list:
                    if item in sorted_subds_list[i]:
                        flag += 1
                if flag == 0:
                    optimized_list.append(sorted_subds_list[i])

    # removing '.' at the beginning of each subdomain (not necessary anymore).
    for i, element in enumerate(optimized_list):
        optimized_list[i] = element.strip('.')

    # returning elements in alphabetical order.
    sorted_optimized_list = []
    sorted_optimized_list.extend(sorted(optimized_list, key=len))
    #!TODO BEGIN DEL TEST
    from datetime import datetime
    base_dir = f'/tmp/'
    ftimestamp = datetime.now().strftime('%y%m%d-%H%M%S')
    test_file = f'{base_dir}{ftimestamp}-test_subsort-sorted_optimized_list-append_list'
    with open(test_file, 'a') as f:
        for item in sorted_optimized_list:
            f.write(item + '\n')
    #!TODO END DEL TEST
    return sorted_optimized_list


def del_file_subds_redund(subds_file):
    subds_list = []
    with open(subds_file, 'r') as lfp:
        for line in lfp:
            # add '.' at the beginning of each subdomain to
            # appropriately test subdomains occurrences in logic parsing.
            subds_list.append('.' + line.strip('\n'))
    
    optimized_list = []
    optimized_list.extend(subds_occurrence_logic_check(subds_list))
    return optimized_list


def del_list_subds_redund(subdomains_list):
    subds_list = []
    for element in subdomains_list:
        subds_list.append('.' + element)
    optimized_list = []
    optimized_list.extend(subds_occurrence_logic_check(subds_list))
    return optimized_list


def print_list_elements(list):
    for element in list:
        print(element)


if __name__ == '__main__':

    if args.file:
        optimal_subd_list = []
        optimal_subd_list.extend(del_file_subds_redund(args.file))

        print_list_elements(optimal_subd_list)
