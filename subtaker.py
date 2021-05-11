
# LEGAL WARNING: DO NOT USE THIS TOOL ON WEBSITES YOU DON'T HAVE PERMISSION.

# I created this project with the objective to learn python, OO, networking, and 
# ethical hacking, simultaneously.

# Feel free to branch and do push requests with improvements as you see fit. 
# They are a great opportunity for me to learn so they're very welcome.

# Also, big thanks to Patrik Hudak, as this project had a lot of contribution from 
# his website and master's thesis.

# I encourage anyone interested in leraning about subdomain takeover vulnerabilities
# to check his posts: https://0xpatrik.com/


import os
import sys
import subprocess
from termcolor import colored
from more_itertools import unique_everseen
import argparse

import modules.amass_enum
import modules.fdns
import modules.massdns
import modules.subsort
import modules.takeover
import modules.utils


#! Argparse: command line arguments
# flags: https://docs.python.org/3/library/argparse.html?highlight=add_argument#argparse.ArgumentParser.add_argument
parser = argparse.ArgumentParser(description='Subtaker: subdomain takeover tool.')

parser.add_argument('-f', type=str, metavar='<file>',
    help='List domains in a \'.txt\' file. Each domain must be in a different line. Do not include \'http://\' or \'https://\'. Usage: -f domains.txt')

# Getting working directory as default for report output path
argparse_default_o = subprocess.run(['pwd'], capture_output=True, text=True).stdout.strip()
parser.add_argument('--out-dir', type=str, metavar='<dir_path>', default=argparse_default_o,
    help='Directory base path to output report files. Usage: -o /path/to/dir/')

parser.add_argument('--amass-enum', action='store_true',
    help='Do subdomain enumeration with amass')

parser.add_argument('--fdns', type=str, metavar='<file.json.gz>',
    help='Path to the file containing Forward DNS data (do NOT extract the file). See \'opendata.rapid7.com\'. Usage: --fdns cname_file.json.gz')

parser.add_argument('--brute', type=str, metavar='<file>',
    help='Bruteforce subdomains. Usage: -b wordlist.txt')

parser.add_argument('--concurrent', type=int, metavar='<number>', default=10000, help='Number of concurrent DNS lookups. Default is 10,000. Usage: --concurrent 5000')

#TODO parser.add_argument('--rdns', type=str, metavar='', help='Reverse DNS') #TODO Reverse DNS query


args = parser.parse_args()

# Adding '/' to end of args.out_dir path, if not already at the end
if args.out_dir[-1] != '/':
    args.out_dir += '/'


# Functions
def get_script_dir():
    path = os.path.realpath(sys.argv[0])
    if os.path.isdir(path):
        return path
    else:
        return os.path.dirname(path)

def get_resolvers_dir():
    return get_script_dir()+"/dns-resolvers/" # Active/reliable DNS resolvers dir

def get_resolvers_fpath():
    return get_script_dir()+"/dns-resolvers/resolvers.txt" # Active/reliable DNS resolvers file


# Cewl h4x0r b4nn3r :]
print('''
███████╗██╗   ██╗██████╗ ████████╗ █████╗ ██╗  ██╗███████╗██████╗ 
██╔════╝██║   ██║██╔══██╗╚══██╔══╝██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
███████╗██║   ██║██████╔╝   ██║   ███████║█████╔╝ █████╗  ██████╔╝
╚════██║██║   ██║██╔══██╗   ██║   ██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗
███████║╚██████╔╝██████╔╝   ██║   ██║  ██║██║  ██╗███████╗██║  ██║
╚══════╝ ╚═════╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
  _               _ _          _ _                _    
 | |             (_) |        (_) |              | |   
 | |__  _   _     _| |_  ____  _| |__   __ _  ___| | __
 | '_ \| | | |   | | __||____|| | '_ \ / _` |/ __| |/ /
 | |_) | |_| |   | | |_       | | | | | (_| | (__|   < 
 |_.__/ \__, |   |_|\__|     _| |_| |_|\__,_|\___|_|\_\ 
        |___/               |___/                      
''')

print("\nLEGAL WARNING:\tDO NOT USE THIS TOOL ON ASSETS YOU DON'T HAVE PERMISSION!\n"
    + "\t\tPROCEED AT YOUR OWN RESPONSIBILITY!")


# 0.1 Updating resolvers
resolvers_f = get_resolvers_fpath()
try:
    subprocess.run(['rm', resolvers_f])
except FileNotFoundError:
    pass

try:
    # Fresh list of periodically validated public DNS resolvers.
    subprocess.run(['wget', '--no-verbose', 'https://raw.githubusercontent.com/janmasarik/resolvers/master/resolvers.txt',
        '-P', get_resolvers_dir()])

    modules.utils.screen_msg("DNS resolvers file updated successfully!\n")
except Exception:
    modules.utils.screen_msg(f"resolvers file could not be updated at {get_resolvers_dir()}")


# Timestamp for file names
ftimestamp = modules.utils.get_time_yymmdd_hhmmss()

# Base file path
base_filepath = f'{args.out_dir}{ftimestamp}'


# Main domains to grep subdomains from
grep_domains_list = []

with open(args.f, 'r') as domain_file:
    for domain in domain_file:
        grep_domains_list.append(domain.strip('\n'))
    
# Removing main domains that are redundant for grep
grep_domains_list = modules.subsort.del_list_subds_redund(grep_domains_list)


# This list will be dns resolved
subdomains_list = []

#! '!' means 'important step'
#! Use Amass to get passive data on each domain

if args.amass_enum:
    for domain in grep_domains_list:
        modules.utils.screen_msg(f'Executing: amass enum --passive -d {domain}')
        subdomains_list.extend(list(unique_everseen(modules.amass_enum.run_amass_enum(domain))))

    subdomains_list = list(unique_everseen(subdomains_list))
    print()


#! Retrieve subdomains from FDNS related to inscope domains
if args.fdns:
    modules.utils.screen_msg(f'Grepping for subdomains on file: {args.fdns}')
    print('\n> Always remember to check for FDNS file UPDATES on:')
    print(colored('  https://opendata.rapid7.com/sonar.fdns_v2/\n', 'green'))
    
    fdns_output = []
    for domain in grep_domains_list:
        modules.utils.screen_msg(f'Grepping \'{domain}\'')
        fdns_output.extend(modules.fdns.grep_subd_fdns(domain, args.fdns))
        fdns_output = list(unique_everseen(fdns_output))
    
    modules.utils.screen_msg(f'FDNS grep ended succesfully! '
        + f'{modules.utils.count_new_unique(subdomains_list, fdns_output):,d}'
        + ' new subdomains discovered from a total of '
        + f'{len(fdns_output):,d}'
        + ' found on .json.gz file.')
    
    print()#TODO DEL
    print(f'len(subdomains_list) == {len(subdomains_list):,d}')#TODO DEL
    print(f'len(fdns_output) == {len(fdns_output):,d}')#TODO DEL
    subdomains_list = modules.utils.merge_lists(subdomains_list, fdns_output)
    print(f'subdomains_list = modules.utils.merge_lists(subdomains_list, fdns_output)')#TODO DEL
    print(f'len(subdomains_list) == {len(subdomains_list):,d}')#TODO DEL
    print(f'len(fdns_output) == {len(fdns_output):,d}')#TODO DEL
    
    #!TODO BEGIN DEL TEST
    from datetime import datetime
    base_dir = f'/tmp/'
    testftimestamp = datetime.now().strftime('%y%m%d-%H%M%S')
    test_file = f'{base_dir}{testftimestamp}-test_fdns_output-append_list'
    with open(test_file, 'a') as f:
        for item in fdns_output:
            f.write(item + '\n')
    #!TODO END DEL TEST
    del fdns_output


#! Bruteforce
if args.brute:
    print()
    modules.utils.screen_msg(f'Generating brute-force subdomains using wordlist at: {args.brute}')

    for domain in grep_domains_list:
        brute_sublist = []
        with open(args.brute, 'r') as f:
            for line in f:
                brute_sublist.append(line.strip('\n') + '.' + domain)
        subdomains_list.extend(brute_sublist)
        
    print(f'len(subdomains_list == {len(subdomains_list):,d}')#TODO DEL
    subdomains_list = list(unique_everseen(subdomains_list))
    print('subdomains_list = list(unique_everseen(subdomains_list))')#TODO DEL
    print(f'len(subdomains_list == {len(subdomains_list):,d}')#TODO DEL
    del brute_sublist

        # subdomains_list = modules.utils.merge_lists(subdomains_list, brute_list) #TODO DEL
        
        #!TODO BEGIN DEL TEST
        # from datetime import datetime
        # base_dir = f'/tmp/'
        # testftimestamp = datetime.now().strftime('%y%m%d-%H%M%S')
        # test_file = f'{base_dir}{testftimestamp}-test_brute_list-append_list'
        # with open(test_file, 'a') as f:
        #     for item in brute_list:
        #         f.write(item + '\n')
        #!TODO END DEL TEST
        # del brute_list


#! Massdns: resolve subdomains
print()
modules.utils.screen_msg(f'Starting Massdns on {len(subdomains_list):,d} possible subdomains'
    + f' with {args.concurrent:,d} concurrent DNS lookups.')


# massdns output files path
massdns_ndjson_outpf = f'{args.out_dir}{ftimestamp}-massdns.ndjson'
massdns_txt_subds_outpf = f'{args.out_dir}{ftimestamp}-massdns-subds.txt'


# Exec massdns and dump results on output file
modules.massdns.massdns_dump(subdomains_list, resolvers_f, args.concurrent, massdns_ndjson_outpf)

#!TODO BEGIN DEL TEST
from datetime import datetime
base_dir = f'/tmp/'
testftimestamp = datetime.now().strftime('%y%m%d-%H%M%S')
test_file = f'{base_dir}{testftimestamp}-test_subdomains_list-append_list'
with open(test_file, 'a') as f:
    for item in subdomains_list:
        f.write(item + '\n')
#!TODO END DEL TEST
del subdomains_list

# Writing massdns simplified subdomains txt file
massdns_txt_subds_l = [] # l == list
massdns_txt_subds_l.extend(modules.massdns.grep_subds_ndjson(massdns_ndjson_outpf))

modules.utils.append_list_file(massdns_txt_subds_l, massdns_txt_subds_outpf)


# Massdns Stats
line_count = modules.utils.count_lines(massdns_ndjson_outpf)

cname_count = subprocess.run(['grep', '-c', 'CNAME', massdns_ndjson_outpf],
    capture_output=True)

mx_count = subprocess.run(['grep', '-c', 'MX', massdns_ndjson_outpf],
    capture_output=True)

modules.utils.screen_msg('Massdns finished!\n'
    + f'\t{line_count:,d} total records retrieved\n'
    + f'\t{int(cname_count.stdout):,d} CNAME records\n'
    + f'\t{int(mx_count.stdout):,d} MX records')

#! Takeover: 
    # Httprobe requests subdomains list and returns urls
    # Nuclei checks urls for 'takeovers' yaml templates

# First, update Nuclei templates
print()
modules.utils.screen_msg('Updating Nuclei templates')
modules.takeover.update_nuclei_templates()

# Nuclei output file path
nuclei_outpf = f'{args.out_dir}{ftimestamp}-possible-takeovers.txt'

# Then, run nuclei
print()
modules.utils.screen_msg('Running nuclei: testing for subdomain takeover')
modules.takeover.get_nuclei(massdns_txt_subds_outpf,
    nuclei_outpf,
    resolvers_f)

# Getting n of possible takeovers
takeovers_int = 0
try:
    takeovers_int += modules.utils.count_lines(nuclei_outpf)

# Nuclei does not create a file if no result was found
except FileNotFoundError:
    takeovers_int += 0

print()
modules.utils.screen_msg('Subtaker scan finished!\n'
    + f'\t{takeovers_int:,d} results found'
    + f'\tReport files base path: {base_filepath}')
