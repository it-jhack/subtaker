
# LEGAL WARNING: DO NOT USE THIS TOOL ON WEBSITES YOU DON'T HAVE PERMISSION.

#-------------------------------------------------------------------------
# DISCLAIMER: AT THE TIME OF THE INITIAL COMMIT, THE CODE BELOW LACKS 
# MANY GOOD PRACTICES AND IT'S ALSO NOT FULLY OPTIMIZED PERFORMANCE-WISE.
#-------------------------------------------------------------------------

# I created this project as an objective to learn python without worrying about good practices.
# Although I know good practices are a MUST, I tried to make this program as quickly as possible
# to get it running and potentially find vulnerabilities on Bug Bounty Programs ASAP.
# I also didn't have the initial intention to make this project public, but here it is anyway.

# I will eventually find the time to make the whole project cleaner. It just so happens not
# to be my life priority right now.

# Feel free to branch and push request it with good practices and optimizations. They are very welcome :)

# Also, big thanks to Patrik Hudak, as this project had a lot of contribution from his website and master's thesis.
# I encourage anyone interested in this project to check his posts: https://0xpatrik.com/


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

def get_nuclei(grep_domains_list, output_file):
    #shell cmd: nuclei -c 10 -l $grep_DOMAINS_LIST -t subdomain-takeover -nC -o $OUTPUT_FILE
    nuclei_cmd = [
        'nuclei', 
        '-c', '10', # default=10
        '-l', grep_domains_list,
        '-t', 'subdomain-takeover'
        '-nC', # no colors
        '-o', output_file
    ]

    processed = []
    for line in _exec_and_readlines(nuclei_cmd, domains):
        if not line:
            continue
        processed.append(line)
    
    return processed

def print_memory():
    cmd = ['free', '-h']
    p = subprocess.run(cmd, capture_output=True, text=True)
    print(f'\n{p.stdout}')

def email_simple(title, email_body):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASS)
        
        subject = title
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        body = f"{timestamp}{email_body}"
        msg = f'Subject: {subject}\n\n{body}'
        smtp.sendmail(EMAIL_ADDRESS, DEST_ADDRESS, msg)

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



    if p.stdout:
        cnames_bruteforced_list += [cname for cname in p.stdout.split('\n') if cname not in cnames_all_found_list]
        cnames_all_found_list.extend(p.stdout.split('\n'))
        with open(input_for_httpx_file, 'a') as f:
            f.write(p.stdout) # no need for "f.write('\n')" anywhere (TESTED!)
    
    #! Writing the report for BRUTEFORCED ONLY cnames, for each time of execution (and not all time record)
    cnames_bruteforced_file = f'{HOME}/subtaker/subprocessing-outputs/alias_cnames-bruteforced-txt/{ftimestamp}-{company_name}-brutef-alias_cnames.txt'
    
    cnames_bruteforced_list = list(unique_everseen(cnames_bruteforced_list))

    if '' in cnames_bruteforced_list:
        cnames_bruteforced_list.remove('')

    with open(cnames_bruteforced_file, 'a') as f:
        for cname in cnames_bruteforced_list:
            f.write(f'{cname}\n')

    del cnames_bruteforced_list

    
    cnames_all_found_file = f'{HOME}/subtaker/subprocessing-outputs/alias_cnames-all-txt/{ftimestamp}-{company_name}-all-alias_cnames.txt'

    cnames_all_found_list = list(unique_everseen(cnames_all_found_list))

    if '' in cnames_all_found_list:
        cnames_all_found_list.remove('')


    with open(cnames_all_found_file, 'a') as f:
        for cname in cnames_all_found_list:
            f.write(f'{cname}\n')


    del cnames_all_found_list

    #! Writing the report of found valid all subdomains (including A) for #123
    # Not appending repetitions
    subds_all_found_list = []

    #! enhancement: make function
    # each subd on this list will be verified if already in company all discovered cnames
    # if subd not already in file (that is, if really new) it is appended to file
    

    del p
    p = subprocess.run([f'grep NOERROR {NDJ_OUTP_1}\
    | jq -crM \'.data | .answers | .[] | .name\'\
    | sort\
    | uniq'],
        shell=True, capture_output=True, text=True)
    
    if p.stdout:
        subds_all_found_list.extend(p.stdout.split('\n'))

    del p
    p = subprocess.run([f'grep NOERROR {NDJ_OUTP_2}\
    | jq -crM \'.data | .answers | .[] | .name\'\
    | sort\
    | uniq'],
        shell=True, capture_output=True, text=True)
    
    if p.stdout:
        subds_all_found_list.extend(p.stdout.split('\n'))

    del p
    p = subprocess.run([f'grep NOERROR {NDJ_OUTP_3}\
    | jq -crM \'.data | .answers | .[] | .name\'\
    | sort\
    | uniq'],
        shell=True, capture_output=True, text=True)

    subds_bruteforced_list = []
    
    if p.stdout:
        subds_bruteforced_list += [subd for subd in p.stdout.split('\n') if subd not in subds_all_found_list]
        subds_all_found_list.extend(p.stdout.split('\n'))
    
    subds_all_found_file = f'{HOME}/subtaker/subprocessing-outputs/subds-all-txt/{ftimestamp}-{company_name}-all-subds.txt'

    subds_all_found_list = list(unique_everseen(subds_all_found_list))

    if '' in subds_all_found_list:
        subds_all_found_list.remove('')

    with open(subds_all_found_file, 'a') as f:
        for subd in subds_all_found_list:
            f.write(f'{subd}\n')

    #! enhancement: apply function also for step 5 (and write to company's file if new)
    if bruteforce_question == 'n':
        print()
        
        #! Enhancement: make function
        #Eliminating duplicates in input_for_httpx_file (in case #1 #2 #3 and #5 found the same record):
        del p
        p = subprocess.run([f'cat {input_for_httpx_file} | grep -F . | sort | uniq'],
            shell=True, capture_output=True, text=True)

        with open(input_for_httpx_file, 'w') as f:
            f.write(p.stdout)

    else:

        #! Appending to report of ALL subdomains found on step #5
        del p
        p = subprocess.run([f'grep NOERROR {NDJ_OUTP_5}\
        | jq -crM \'.data | .answers | .[] | .name\'\
        | sort\
        | uniq'],
            shell=True, capture_output=True, text=True)
        
        #! Writing the report of found valid all subdomains (including A) for #5
        # Not appending repetitions
        if p.stdout:
            subds_bruteforced_list += [subd for subd in p.stdout.split('\n') if subd not in subds_all_found_list]
            subds_all_found_list.extend(p.stdout.split('\n'))

        subds_bruteforced_file = f'{HOME}/subtaker/subprocessing-outputs/subds-bruteforced-txt/{ftimestamp}-{company_name}-brutef-subds.txt'

        subds_bruteforced_list = list(unique_everseen(subds_bruteforced_list))

        if '' in subds_bruteforced_list:
            subds_bruteforced_list.remove('')

        with open(subds_bruteforced_file, 'a') as f:
            for subdomain in subds_bruteforced_list:
                f.write(f'{subdomain}\n')

        del subds_bruteforced_list

        subds_all_found_list = list(unique_everseen(subds_all_found_list))

        if '' in subds_all_found_list:
            subds_all_found_list.remove('')

        with open(subds_all_found_file, 'a') as f:
            for subd in subds_all_found_list:
                f.write(f'{subd}\n')

        del subds_all_found_list
        #! end

        #! Enhancement: make function (same in "fdns_skip =='y'" condition a few lines above)
        #Eliminating duplicates in input_for_httpx_file (in case #1 #2 #3 and #5 found the same record):
        time_now = str(datetime.now().strftime('%H:%M'))
        print(f'{time_now}: {lineno()}') #!del
        p = subprocess.run([f'cat {input_for_httpx_file} | grep -F . | sort | uniq'],
            shell=True, capture_output=True, text=True)

        with open(input_for_httpx_file, 'w') as f:
            f.write(p.stdout)

    #removing blacklisted false-positives
    blacklist_file = f'{HOME}/subtaker/false-pos-blacklist/blacklist.txt'

    blacklist = []
    
    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now}: {lineno()}') #!del

    with open(blacklist_file, 'r') as f:
        for line in f:
            blacklist.append(line.strip('\n'))

    while '' in blacklist:
        blacklist.remove('')

    input_for_httpx_list = []
    
    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now}: {lineno()}') #!del

    with open(input_for_httpx_file, 'r') as f:
        for line in f:
            flag = 0
            for item in blacklist:
                if item in line:
                    flag += 1
            if flag == 0:
                input_for_httpx_list.append(line.strip('\n'))

    del blacklist

    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now}: {lineno()}') #!del

    with open(input_for_httpx_file, 'w') as f:
        f.write('')

    with open(input_for_httpx_file, 'a') as f:
        for item in input_for_httpx_list:
            f.write(f'{item}\n')

    del input_for_httpx_list

    # httpx to serve as input to nuclei
        
    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now}: {lineno()}') #!del

    httpx_cmd = f'httpx -l {input_for_httpx_file} -silent'

        
    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now}: subprocessing: httpx') #!del

    p_httpx = subprocess.run([httpx_cmd],
        shell=True, capture_output=True, text=True)

    httpx_outp_list = []
    httpx_outp_list.extend(p_httpx.stdout.split('\n'))

        
    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now}: {lineno()}') #!del
    
    httpx_outp_list = list(unique_everseen(httpx_outp_list))

    if '' in httpx_outp_list:
        httpx_outp_list.remove('')

    nuclei_input_file = f'{HOME}/subtaker/subprocessing-outputs/7_b_inputs-for-nuclei/{ftimestamp}-{company_name}-input_for_nuclei.txt'

    with open(nuclei_input_file, 'a+') as f:
        for item in httpx_outp_list:
            f.write(f'{item}\n')

    del httpx_outp_list

    # 8. Nuclei subprocess of fingerprint verification
    nuclei_outp_file = f'{HOME}/subtaker/subprocessing-outputs/7_c_nuclei-outp/{ftimestamp}-{company_name}-nuclei_output.txt'
    
    nuclei_cmd = f'nuclei -l {nuclei_input_file} \
        -t subdomain-takeover/detect-all-takeovers.yaml \
        -t dns/azure-takeover-detection.yaml\
        -o {nuclei_outp_file} -silent -pbar'

    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now} > subprocessing: nuclei')
    print(f'      > report will be saved on:')
    print(colored(f'      subprocessing-outputs/7_c_nuclei-outp/_report.txt', 'blue'))
    print()

    p_nuclei = subprocess.run([nuclei_cmd],
        shell=True)
        

    REPORT = f'{HOME}/subtaker/subprocessing-outputs/7_c_nuclei-outp/_report.txt'
    
    stdout_list = []
    possible_positives_list = []

    if not os.path.exists(nuclei_outp_file):
        time_now = str(datetime.now().strftime('%H:%M'))
        print()
        print(f'{time_now} > Nuclei returned NO vulnerable subdomains for {company_name}')

    else:
        with open(nuclei_outp_file, 'r') as nuclei_outpf:
            nuclei_outp_content = nuclei_outpf.read()

        stdout_list.extend(nuclei_outp_content.split('\n'))
            
            

        # 9. Parsing nuclei output file, and emailing me possible positives

        pattern_subd = re.compile('https?:\/\/(.*)')

        if stdout_list:
            for item in stdout_list:
                possible_positives_list.append(item)

        del stdout_list

        possible_positives_ebody = ''

        if possible_positives_list: # if list has something (NOT empty)
            if len(possible_positives_list) <= 20:
                for item in possible_positives_list:
                    if item:
                        possible_positives_ebody += f'\n----------------------------------------'
                        possible_positives_ebody += f'\nNUCLEI OUTPUT: {item}\n\n'
                        
                        matches_subd = pattern_subd.finditer(item)
                        
                        for match in matches_subd:
                            
                            subd = match.group(1).strip('/')
                            # print(subd)

                            p_dig_short = subprocess.run([f'dig +short {subd}'],
                                shell=True, capture_output=True, text=True)
                            
                            p_dig = subprocess.run([f'dig {subd}'],
                                shell=True, capture_output=True, text=True)
                            
                            possible_positives_ebody += p_dig_short.stdout
                            possible_positives_ebody += p_dig.stdout
            else:
                possible_positives_ebody += f'{len(possible_positives_list)} positives found.'
            
            if possible_positives_ebody:
                # email yourself
                email_simple(f'SUBD TKO on {company_name}', possible_positives_ebody)
                
                # Writing report
                with open(REPORT, 'a') as f:
                    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    f.write('\n\n########################################\n')
                    f.write(f'COMPANY: {company_name}\n')
                    f.write(f'TIMESTAMP: {timestamp}\n')
                    f.write('########################################\n')
                    f.write(f'{possible_positives_ebody}\n')

    del possible_positives_list

    # 10. Moving finished inscope_file
    inscopef_mv_destination = f'{HOME}/subtaker/inscopes/done/'

    p = subprocess.run([f'mv {inscope_file} {inscopef_mv_destination}'],
        shell=True)

    log_csv_file = f'{HOME}/subtaker/log-inscopes.csv'
    with open(log_csv_file, 'a') as logf:
        
        massdns_res_rate_int = int(massdns_res_rate_str)

        end_time = datetime.now()
        total_time = end_time - start_time
                
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        #replacing comma-thousand-separators by dot-separators, so it doesn't mess the csv log
        #! enhancement: create a function for this
        massdns_count_total = f'{massdns_count_total:,d}'
        massdns_count_total = massdns_count_total.replace(',','.')

        massdns_res_rate_sec = int(massdns_res_rate_sec)
        massdns_res_rate_sec = f'{massdns_res_rate_sec:,d}'
        massdns_res_rate_sec = massdns_res_rate_sec.replace(',','.')

        massdns_res_rate_min = int(massdns_res_rate_min)
        massdns_res_rate_min = f'{massdns_res_rate_min:,d}'
        massdns_res_rate_min = massdns_res_rate_min.replace(',','.')

        massdns_res_rate_int = f'{massdns_res_rate_int:,d}'
        massdns_res_rate_int = massdns_res_rate_int.replace(',','.')

        logf.write(f'{timestamp},{company_name},{total_time},{massdns_count_total},{massdns_res_rate_sec},{massdns_res_rate_min},{massdns_res_rate_int},{bruteforce_question},{bruteforce_fast}\n')

print('\n###########################################')
time_now = str(datetime.now().strftime('%H:%M'))
print(f'{time_now} > PROGRAM TERMINATED')
print('###########################################')