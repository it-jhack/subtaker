
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
from datetime import datetime
import json
import ndjson
import smtplib
from termcolor import colored
import re
from more_itertools import unique_everseen
import inspect
import argparse

import modules.utils
import modules.subsort
import modules.fdns


# Argparse 
# flags: https://docs.python.org/3/library/argparse.html?highlight=add_argument#argparse.ArgumentParser.add_argument
parser = argparse.ArgumentParser(description='Subtaker: subdomain takeover tool.')

input_group = parser.add_mutually_exclusive_group()
input_group.add_argument('-f', type=str, metavar='<file>', help='List domains in a \'.txt\' file. Each domain must be in a different line. Do not include \'http://\' or \'https://\'. Usage: -f domains.txt')

# Getting working directory as default for report output
argparse_default_o = subprocess.run(['pwd'], capture_output=True, text=True).stdout.strip()

parser.add_argument('--out-dir', type=str, metavar='<dir_path>', default=argparse_default_o, help='Directory base path to output report files. Usage: -o /path/to/dir/')
parser.add_argument('--brute', type=str, metavar='<file>', help='Bruteforce subdomains. Usage: -b bruteforcelist.txt')
parser.add_argument('--concurrent', type=int, metavar='<number>', default=10000, help='Number of concurrent DNS lookups. Default is 10,000. Usage: --concurrent 5000')
parser.add_argument('--fdns', type=str, metavar='<file.json.gz>', help='Path to the file containing Forward DNS data (do NOT extract the file). See \'opendata.rapid7.com\'. Usage: --fdns cname_file.json.gz')
# parser.add_argument('--rdns', type=str, metavar='', help='Reverse DNS') #TODO Reverse DNS query

args = parser.parse_args()

# Adding '/' to end of dir path, if not already at the end
if argparse.out_dir[-1] != '/':
    argparse.out_dir += '/'


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

print("\nLEGAL WARNING: DO NOT USE THIS TOOL ON WEBSITES YOU DON'T HAVE PERMISSION!\n")


# 0.1 Updating resolvers
try:
    subprocess.run(['rm', get_resolvers_fpath()])
except FileNotFoundError:
    pass

try:
    # Fresh list of periodically validated public DNS resolvers.
    subprocess.run(['wget', 'https://raw.githubusercontent.com/janmasarik/resolvers/master/resolvers.txt',
        '-P', get_resolvers_dir()])

    modules.utils.screen_msg("updated resolvers file successfully")
except Exception:
    modules.utils.screen_msg(f"resolvers file could not be updated at {get_resolvers_dir()}")


print('\n> Always remember to check for FDNS file UPDATES on:')
print(colored('  https://opendata.rapid7.com/sonar.fdns_v2/\n', 'blue'))

grep_domains_list = []

with open(argparse.f, 'r') as domain_file:
    for domain in domain_file:
        grep_domains_list.append(domain)
    
# Removing main domains redundant for grep
grep_domains_list = modules.subsort.del_list_subds_redund(grep_domains_list)


#! '!' means 'important!'
#! Use Amass to get passive data on each domain
amass_output = []
for domain in grep_domains_list:
    modules.utils.screen_msg('Executing: amass enum --passive -d')
    amass_output.extend(list(unique_everseen(modules.amass_enum(domain))))

# This list will be dns resolved
subdomains_list = []

subdomains_list = amass_output
del amass_output


#! Retrieve subdomains from FDNS related to inscope domains
if argparse.fdns:
    modules.utils.screen_msg(f'Grepping {argparse.fdns} for subdomains')
    
    fdns_output = []
    fdns_output.extend(modules.fdns.grep_fdns(grep_domains_list, argparse.fdns))
    fdns_output = list(unique_everseen(fdns_output))
    
    modules.utils.screen_msg(f'FDNS grep ended succesfully! '
        + f'{modules.utils.count_new_unique(subdomains_list, fdns_output):,d}'
        + ' new subdomains discovered from a total of '
        + f'{len(fdns_output):,d}'
        + ' found on .json.gz file.')
    subdomains_list = modules.utils.merge_lists(subdomains_list, fdns_output)
    del fdns_output


#! Bruteforce
brute_list = []
if argparse.brute:
    modules.utils.screen_msg(f'Subdomain brute-forcing using list file: {argparse.brute}')
    
    with open(argparse.brute, 'r') as brute_file:
        for line in brute_file:
            for domain in grep_domains_list:
                brute_list.append(line + '.' + domain)
        
        subdomains_list = modules.utils.merge_lists(subdomains_list, brute_list)
        del brute_list
                

#! Massdns: resolve subdomains

modules.utils.screen_msg(f'Starting MassDNS on {len(subdomains_list):,d} possible subdomains'
    + f' with {argparse.concurrent:,d} concurrent DNS lookups.')

# Exec massdns
output = get_massdns(subdomains_list, get_resolvers_fpath(), argparse.concurrent)

del subdomains_list

# write massdns resolution .ndjson output file
massdns_ndjson_output_file = f'{argparse.out_dir}{modules.utils.get_time_yymmdd_hhmmss()}-massdns.ndjson'

modules.utils.write_full_output(massdns_ndjson_output_file, output)

del output

# Stats
line_count = modules.utils.count_lines(massdns_ndjson_output_file)

cname_count = subprocess.run(['grep', '-c', 'CNAME', massdns_ndjson_output_file],
    capture_output=True)

mx_count = subprocess.run(['grep', '-c', 'MX', massdns_ndjson_output_file],
    capture_output=True)

modules.utils.screen_msg('MassDNS finished!\n'
    + f'\t{line_count:,d} total records retrieved\n'
    + f'\t{cname_count:,d} CNAME records\n'
    + f'\t{mx_count:,d} MX records'
