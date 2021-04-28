
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


HOME = os.environ.get('HOME')


# Environment Variables
EMAIL_ADDRESS = os.environ.get('SUBT_EMAIL_USER') # SUBT = subtaker
EMAIL_PASS = os.environ.get('SUBT_EMAIL_APP_PASS') # Recommended NOT to use your real password. See: youtu.be/JRCJ6RtE3xU?t=54
DEST_ADDRESS = os.environ.get('SUBT_EMAIL_RECEIVER') # This is the email that will get the notification

def lineno():
    # Returns the current line number in the code
    # ex.: print("hello, this is line number ", lineno())
    return inspect.currentframe().f_back.f_lineno

def _exec_and_readlines(cmd, domains):

    domains_str = bytes('\n'.join(domains), 'ascii')
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)
    stdout, stderr = proc.communicate(input=domains_str)

    return [j.decode('utf-8').strip() for j in stdout.splitlines() if j != b'\n']

massdns_res_rate_str = '500' # High resolution rate may blacklist your IP on DNS server.
def get_massdns(domains):
    massdns_cmd = [
        f'{HOME}/massdns/bin/massdns',
        '--quiet',
        '-s', massdns_res_rate_str,
        '-t', 'A',
        '-o', 'J',
        '-r', RESOLVERS_FPATH,
        '--flush'
    ]

    processed = []
    for line in _exec_and_readlines(massdns_cmd, domains):
        if not line:
            continue
        processed.append(json.loads(line.strip()))
    
    return processed

# Avoid memory killed when resolving/bruteforcing millions of subdomains
def massdns_sliced_list(subdomains, outp_file):
    max_amount = 1_000_000
    with open(outp_file, 'a') as f:
        while len(subdomains) > max_amount:
            ndjson.dump(get_massdns(subdomains[:max_amount]), f)
            f.write('\n')
            del subdomains[:max_amount]
        ndjson.dump(get_massdns(subdomains), f)
        del subdomains


def get_amass(domain):
    amass_cmd = [
        'amass', 
        'enum',
        '--passive',
        '-d', domain
    ]

    processed = []
    for line in _exec_and_readlines(amass_cmd, domain):
        if not line:
            continue
        processed.append(line)
    
    return processed

def get_nuclei(domains_list, output_file):
    #shell cmd: nuclei -c 10 -l $DOMAINS_LIST -t subdomain-takeover -nC -o $OUTPUT_FILE
    nuclei_cmd = [
        'nuclei', 
        '-c', '10', # default=10
        '-l', domains_list,
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
    return get_script_dir()+"/resolvers/" # Active/reliable DNS resolvers dir

def get_resolvers_fpath():
    return get_script_dir()+"/resolvers/resolvers.txt" # Active/reliable DNS resolvers file

def get_time_hhmm():
    return datetime.now().strftime('%H:%M')

def screen_msg(message):
    print(f'{get_time_hhmm()} {message}')


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

    screen_msg("updated resolvers file successfully")
except Exception:
    screen_msg(f"resolvers file could not be updated at {get_resolvers_dir()}")


print('\n> Always remember to check for FDNS file UPDATES on:')
print(colored('  https://opendata.rapid7.com/sonar.fdns_v2/\n', 'blue'))

bruteforce_question = str(input('''> Bruteforce subdomains? (y/n): '''))

if bruteforce_question == 'y':
    bruteforce_fast = str(input('''      > Use fast bruteforcing? (y/n): '''))
else:
    bruteforce_fast = 'n/a'


# 0.2 Batching multiple files
to_check_dir = f'{HOME}/subtaker/inscopes/to-check/'

inscope_filenames = []
inscope_filenames.extend(os.listdir(f'{to_check_dir}'))
inscope_filenames.sort()

inscope_filepaths = []
for filename in inscope_filenames:
    file_path = f'{to_check_dir}{filename}'
    inscope_filepaths.append(file_path)


for filepath in inscope_filepaths:
    start_time = datetime.now()
    inscope_file = filepath
    time_now = str(datetime.now().strftime('%H:%M'))

    ftimestamp = datetime.now().strftime('%y.%m.%d-%H.%M')

    print('\n###########################################')
    print()
    print(f'{time_now} > Subtaker processes started on inscope file: {inscope_file}\n')
    


    # 0.3 Grabbing company's name from inscope file path
    company_name_split_list = []
    company_name_split_list.extend(inscope_file.split('/'))


    company_name = company_name_split_list[-1]
    if '.txt' in company_name:
        company_name_split_list = []
        company_name_split_list.extend(company_name.split('.'))
        company_name = company_name_split_list[0]


    if '-' in company_name:
        company_name_split_list = []
        company_name_split_list.extend(company_name.split('-'))

        company_name = company_name_split_list[0]



    # 1. Use amass to get passive data

    amass_outp_list = []

    with open(inscope_file, 'r') as isl:
        print('-------------------------------------------\n')
        for line in isl:
            if line:
                domain = line.strip('\n')
                time_now = str(datetime.now().strftime('%H:%M'))
                print(f'{time_now} > subprocessing: amass enum --passive -d {domain}')
                amass_outp_list.extend(get_amass(domain))
    time_now = str(datetime.now().strftime('%H:%M'))
    
    amass_outp_list = list(unique_everseen(amass_outp_list))
    
    if '' in amass_outp_list:
        amass_outp_list.remove('')
    
    print()
    print(colored(f'{time_now} > amass subprocess finished: {len(amass_outp_list):,} unique subdomains retrieved', 'yellow'))
    
    amass_outp_file = f'{HOME}/subtaker/subprocessing-outputs/1_amass-txt-outp/{ftimestamp}-{company_name}-amass_outp.txt'

    with open(amass_outp_file, 'a') as aof:
        for subdomain in amass_outp_list:
            aof.write(f'{subdomain}\n')


    print(f'      > amass output saved on:')
    print(colored(f'      {amass_outp_file}', 'blue'))

    print('\n-------------------------------------------\n')

            
    # 2. Retrieve subdomains from FDNS related to inscope domains
        
    FDNS_CNAME_FPATH = f'{HOME}/subtaker/fdns/2020-10-03-1601692175-fdns_cname.json.gz'
    
    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now} > parsing the following FDNS file for related subdomains:')
    print(colored(f'      {FDNS_CNAME_FPATH}', 'blue'))

    grep_list = []
    jq_regex_list = []

    # Removing inscope redundancies for (fdns)grep (thus, saving considerable time!)
    with open(inscope_file, 'r') as isf:
        inscope_list = []
        for line in isf:
            inscope_list.append(line.strip('\n'))
        
        sorted_inscope_list = sorted(inscope_list, key=len)
        inscope_range = len(sorted_inscope_list)

        # Removing redundancies in FDNS grep parsing
        fdns_parsing_input_list = []

        for i in range(inscope_range):
                
            disposable_list = []
            disposable_list.extend(sorted_inscope_list)
            disposable_list.remove(sorted_inscope_list[i])
            disposable_list_string = str(disposable_list)

            if sorted_inscope_list[i] in disposable_list_string:
                flag = 0
                for item in fdns_parsing_input_list:
                    if item in sorted_inscope_list[i]:
                        flag += 1
                if flag == 0:
                    fdns_parsing_input_list.append(sorted_inscope_list[i])
            else:
                disposable_list_string_2 = str(fdns_parsing_input_list)
                if sorted_inscope_list[i] not in disposable_list_string_2:
                    flag = 0
                    for item in fdns_parsing_input_list:
                        if item in sorted_inscope_list[i]:
                            flag += 1
                    if flag == 0:
                        fdns_parsing_input_list.append(sorted_inscope_list[i])


    # turning inscopes into NOT regex strings for 'grep' and 'jq'
    
    for domain in fdns_parsing_input_list:
        scope = domain.strip()
        sliced_scope = scope.split(".")

        grep_str = '.'       
        jq_regex_str = '\\\\.'
        i = 1
        for item in sliced_scope:
            grep_str += item
            jq_regex_str += item
            if i < len(sliced_scope):
                grep_str += '.'
                jq_regex_str += '\\\\.'
                i += 1
        grep_list.append(grep_str)
        jq_regex_list.append(jq_regex_str)

    del fdns_parsing_input_list

    fdns_outp_list = []


    for grep_item, jq_item in zip(grep_list, jq_regex_list):

        time_now = str(datetime.now().strftime('%H:%M'))
        
        print(f'{time_now} > FDNS parsing for: {grep_item} | {jq_item} [grep|jq]')

        p = subprocess.run([f'zcat {FDNS_CNAME_FPATH}\
        | grep -F \'{grep_item}\'\
        | jq -crM \'if (.name | test("{jq_item}")) then .name elif (.value | test("{jq_item}")) then .value else empty end\'\
        | sort\
        | uniq'],
            shell=True, capture_output=True, text=True)

        fdns_outp_list.extend(p.stdout.split('\n'))
        # grep -F = fixed strings (not regex)
        # jq -c = compact instead of pretty-printed output; 
        # -r = output raw strings, not JSON texts; 
        # -M = monochrome (don't colorize JSON);

    fdns_outp_list = list(unique_everseen(fdns_outp_list))
    
    if '' in fdns_outp_list:
        fdns_outp_list.remove('')

    total_subds_fdns_parsed = len(fdns_outp_list)

    # Removing subdomains in FDNS_outp that are already in amass_outp
    fdns_outp_list = [subd for subd in fdns_outp_list if subd not in amass_outp_list]

    total_subds_fdns_non_repeat = len(fdns_outp_list)
    total_subds_fdns_diff = total_subds_fdns_parsed - total_subds_fdns_non_repeat

    fdns_parsing_file = f'{HOME}/subtaker/subprocessing-outputs/2_fdns-parsing-txt-outp/{ftimestamp}-{company_name}-fdns_parsing_results.txt'
    with open(fdns_parsing_file, 'a') as fpf:
        for item in fdns_outp_list:
            fpf.write(f'{item}\n')

    time_now = str(datetime.now().strftime('%H:%M'))
    print(colored(f'{time_now} > FDNS parsing finished: {len(fdns_outp_list):,} subdomains retrieved', 'yellow'))
    print(colored(f'      > {total_subds_fdns_diff:,} excluded because already in amass outp', 'yellow'))

    print('\n-------------------------------------------\n')



    # 3. Generate more possibilities using Commonspeak2 wordlist
    
    if bruteforce_question == 'n':
        cs2_outp_list = []

        time_now = str(datetime.now().strftime('%H:%M'))
        print(f'{time_now} > Bruteforce step: Commonspeak2 wordlist generation skipped')

        print('\n-------------------------------------------\n')

    else:
        cs2_wordlist = []

        if bruteforce_fast == 'y':

            time_now = str(datetime.now().strftime('%H:%M'))
            print(f'{time_now} > parsing wordlist fast variation')

            cs2_wordlist_file = f'{HOME}/subtaker/wordlists/fast_wordlist.txt'
            with open(cs2_wordlist_file, 'r') as f:
                cs2_wordlist = f.read().split('\n')

        else:
            time_now = str(datetime.now().strftime('%H:%M'))
            print(f'{time_now} > parsing wordlist slow variation')

            cs2_wordlist_file = f'{HOME}/subtaker/wordlists/wordlist.txt'
            with open(cs2_wordlist_file, 'r') as f:
                cs2_wordlist = f.read().split('\n')

        cs2_outp_list = []

        with open(inscope_file, 'r') as sf:
            for line in sf:
                scope = line.strip()
                for word in cs2_wordlist:
                    if not word.strip(): 
                        continue
                    cs2_outp_list.append(f'{word.strip()}.{scope}')

        del cs2_wordlist

        cs2_tot_possib_len = len(cs2_outp_list) # line necessary in case I decide to comment out the subbrute process.
        print(colored(f'      > {len(cs2_outp_list):,d} possible subdomains generated by commonspeak2', 'yellow'))

        #! BEGIN: subbruteforce on amass_outp_list
        sub_brute_wordlist_file = f'{HOME}/subtaker/wordlists/superfast_wordlist.txt'
        
        sub_brute_list = []

        with open(sub_brute_wordlist_file, 'r') as f:
            for line in f:
                sub_brute_list.append(line.strip('\n'))


        for subdomain in amass_outp_list:
            for word in sub_brute_list:
                cs2_outp_list.append(f'{word.strip()}.{subdomain.strip()}')

        cs2_outp_list = list(unique_everseen(cs2_outp_list))

        if '' in cs2_outp_list:
            cs2_outp_list.remove('')

        sub_brute_total_len = len(amass_outp_list) * len(sub_brute_list)
        del sub_brute_list
        print(colored(f'      > {sub_brute_total_len:,d} possibilities generated sub-bruteforcing passively found subdomains', 'yellow'))
        
        cs2_tot_possib_len = len(cs2_outp_list)
        #! END: subbruteforce on amass_outp_list
        
        # Removing from bruteforce list if subd already on Amass/FDNS list (to resolve)
        cs2_outp_list = [subd for subd in cs2_outp_list if subd not in amass_outp_list]
        cs2_outp_list = [subd for subd in cs2_outp_list if subd not in fdns_outp_list] # tested: cs2_outp_list will only have subds that are not in both amass and fdns outp
        
        
        cs2_eliminated_count = cs2_tot_possib_len - len(cs2_outp_list)
        print(colored(f'      > {cs2_eliminated_count:,d} possibilities excluded because already in amass/FDNS output', 'yellow'))

    print('\n-------------------------------------------\n')

    #! begin TEMPORARY TEST to see if commonspeak2 output is OK,
    # Delete once in production phase

    cs2_outp_file = f'{HOME}/subtaker/subprocessing-outputs/3_cs2-outp(to-test-if-ok)DEL-AFTER/{ftimestamp}-commonspeak2-outp.txt'

    with open(cs2_outp_file, 'a+') as f:
        for item in cs2_outp_list:
            f.write(f'{item}\n')
    #! end of TEMPORARY TEST (deletion)

    # 4.1 Massdns (resolve) amass_outp_list
    
    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now} > Starting MassDNS on {len(amass_outp_list):,d} possible subdomains from Amass (passive enum) output')
    print(f'      > output will be saved as .ndjson file')

    massdns_count_1 = len(amass_outp_list)

    NDJ_OUTP_1 = f'{HOME}/subtaker/subprocessing-outputs/4_6_massdns_ndjson-outp/{ftimestamp}_1_{company_name}.ndjson'

    massdns_1_time_start = datetime.now()


    massdns_sliced_list(amass_outp_list, NDJ_OUTP_1) # massdns resolution in sliced parts


    massdns_1_time_end = datetime.now()
    
    massdns_1_time_total_sec = int((massdns_1_time_end - massdns_1_time_start).total_seconds())
    
    with open(NDJ_OUTP_1, 'r') as ndj:
        ndj_line_count = 0
        cname_count = 0
        for line in ndj:
            ndj_line_count += 1
            if 'CNAME' in line:
                cname_count += 1
    
    print()
    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now} > MassDNS finished on Amass passive output:')
    print(colored(f'      > {ndj_line_count:,d} total records retrieved', 'yellow'))
    print(colored(f'      > {cname_count:,d} CNAME records retrieved', 'yellow'))

    print('\n-------------------------------------------\n')

    # 4.2 Massdns (resolve) list from FDNS
    
    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now} > starting MassDNS on {len(fdns_outp_list):,d} possible subdomains from FDNS output')
    print(f'      > output will be saved as .ndjson file')

    massdns_count_2 = len(fdns_outp_list)

    NDJ_OUTP_2 = f'{HOME}/subtaker/subprocessing-outputs/4_6_massdns_ndjson-outp/{ftimestamp}_2_{company_name}.ndjson'

    massdns_2_time_start = datetime.now()


    massdns_sliced_list(fdns_outp_list, NDJ_OUTP_2) # massdns resolution in sliced parts


    massdns_2_time_end = datetime.now()
    
    massdns_2_time_total_sec = int((massdns_2_time_end - massdns_2_time_start).total_seconds())
    
    with open(NDJ_OUTP_2, 'r') as ndj:
        ndj_line_count = 0
        cname_count = 0
        for line in ndj:
            ndj_line_count += 1
            if 'CNAME' in line:
                cname_count += 1
    
    print()
    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now} > MassDNS finished on FDNS output:')
    print(colored(f'      > {ndj_line_count:,d} total records retrieved', 'yellow'))
    print(colored(f'      > {cname_count:,d} CNAME records retrieved', 'yellow'))

    print('\n-------------------------------------------\n')

    # 4.3 Massdns (resolve) list from Commonspeak2 ################################################################### 4.3
    
    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now} > starting MassDNS on {len(cs2_outp_list):,d} possible subdomains from CommonSpeak2 output')
    print(f'      > output will be saved as .ndjson file')

    massdns_count_3 = len(cs2_outp_list)

    NDJ_OUTP_3 = f'{HOME}/subtaker/subprocessing-outputs/4_6_massdns_ndjson-outp/{ftimestamp}_3_{company_name}.ndjson'

    massdns_3_time_start = datetime.now()


    massdns_sliced_list(cs2_outp_list, NDJ_OUTP_3) # massdns resolution in sliced parts


    massdns_3_time_end = datetime.now()
    
    massdns_3_time_total_sec = int((massdns_3_time_end - massdns_3_time_start).total_seconds())
    
    with open(NDJ_OUTP_3, 'r') as ndj:
        ndj_line_count = 0
        cname_count = 0
        for line in ndj:
            ndj_line_count += 1
            if 'CNAME' in line:
                cname_count += 1
    
    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now} > MassDNS finished on CommonSpeak2 output:')
    print(colored(f'      > {ndj_line_count:,d} total records retrieved', 'yellow'))
    print(colored(f'      > {cname_count:,d} CNAME records retrieved', 'yellow'))

    print('\n-------------------------------------------\n')

    # 5. DNSGEN on active results from massdns ############################################################ 5
    
    if bruteforce_question == 'n': #! enhancement: create function for resolution_rate calculation
        dnsgen_outp_list = []

        massdns_count_total = massdns_count_1 + massdns_count_2 + massdns_count_3

        massdns_time_total_sec = massdns_1_time_total_sec + massdns_2_time_total_sec + massdns_3_time_total_sec

        # Avoiding division by zero error
        if massdns_time_total_sec == 0:
            massdns_time_total_sec = 1

        massdns_time_total_min = massdns_time_total_sec / 60

        massdns_res_rate_sec = massdns_count_total / massdns_time_total_sec
        massdns_res_rate_min = massdns_count_total / massdns_time_total_min

        all_massdns_res_rate_sec = int(massdns_res_rate_sec)
        all_massdns_res_rate_min = int(massdns_res_rate_min)
        print(colored(f'      > massdns resolution rate = {all_massdns_res_rate_sec:,d} / second', 'green'))
        print(colored(f'                                = {all_massdns_res_rate_min:,d} / minute', 'green'))

        time_now = str(datetime.now().strftime('%H:%M'))
        print(f'{time_now} > Bruteforce step: DNSGEN wordlist generation skipped')

        print('\n-------------------------------------------\n')

    else:
    
        time_now = str(datetime.now().strftime('%H:%M'))
        print(f'{time_now} > starting DNSGEN on .ndjson file')

        dnsgen_list_for_input_file_creation = []

        try: #! enhancement: make function
            p = subprocess.run([f'grep CNAME {NDJ_OUTP_1}\
                | jq -crM \'.data | .answers | .[] | if .type == "CNAME" then .name else empty end\'\
                | sort\
                | uniq'],
                    shell=True, capture_output=True, text=True)

            dnsgen_list_for_input_file_creation.extend(p.stdout.split('\n'))

        except Exception as e:
            print(e)
            continue
        
        try: #! enhancement: make function
            p = subprocess.run([f'grep CNAME {NDJ_OUTP_2}\
                | jq -crM \'.data | .answers | .[] | if .type == "CNAME" then .name else empty end\'\
                | sort\
                | uniq'],
                    shell=True, capture_output=True, text=True)

            dnsgen_list_for_input_file_creation.extend(p.stdout.split('\n'))

        except Exception as e:
            print(e)
            continue

        try: #! enhancement: make function
            p = subprocess.run([f'grep CNAME {NDJ_OUTP_3}\
                | jq -crM \'.data | .answers | .[] | if .type == "CNAME" then .name else empty end\'\
                | sort\
                | uniq'],
                    shell=True, capture_output=True, text=True)

            dnsgen_list_for_input_file_creation.extend(p.stdout.split('\n'))

        except Exception as e:
            print(e)
            continue
        
        dnsgen_list_for_input_file_creation = list(unique_everseen(dnsgen_list_for_input_file_creation))

        if '' in dnsgen_list_for_input_file_creation:
            dnsgen_list_for_input_file_creation.remove('')

        input_for_dnsgen_subproc_file = f'{HOME}/subtaker/subprocessing-outputs/5_txt-inputs-for-dnsgen/{ftimestamp}-input_for_dnsgen-{company_name}.txt' #DELETE THIS FILE AFTER CHECK IF OUTPUT OK

        with open(input_for_dnsgen_subproc_file, 'a') as ifd:
            for item in dnsgen_list_for_input_file_creation:
                ifd.write(f'{item}\n')

        del dnsgen_list_for_input_file_creation #! important massive list to delete and clear RAM

        dnsgen_outp_list = []

        dnsgen_inputf_line_count = 0
        with open(input_for_dnsgen_subproc_file, 'r') as f:
            for line in f:
                dnsgen_inputf_line_count += 1

        if dnsgen_inputf_line_count >= 500: #if bruteforce_fast == 'y':
            time_now = str(datetime.now().strftime('%H:%M')) #! delete
            print(colored(f'{time_now} > running dnsgen --fast', 'yellow')) #! delete
            p = subprocess.run([f'dnsgen --fast {input_for_dnsgen_subproc_file}'],
                shell=True, capture_output=True, text=True)
            
            dnsgen_outp_list.extend(p.stdout.split('\n'))
        else:
            time_now = str(datetime.now().strftime('%H:%M')) #! delete
            print(colored(f'{time_now} > running dnsgen', 'yellow')) #! delete            
            p = subprocess.run([f'dnsgen {input_for_dnsgen_subproc_file}'],
                shell=True, capture_output=True, text=True)
            
            dnsgen_outp_list.extend(p.stdout.split('\n'))

        time_now = str(datetime.now().strftime('%H:%M')) #! delete
        print(colored(f'{time_now} > excluding repetitions', 'yellow')) #! delete

        dnsgen_outp_list = list(unique_everseen(dnsgen_outp_list))

        if '' in dnsgen_outp_list:
            dnsgen_outp_list.remove('')

        time_now = str(datetime.now().strftime('%H:%M'))
        print(colored(f'{time_now} > finished DNSGEN: {len(dnsgen_outp_list):,} possible subdomains generated', 'yellow'))

        dnsgen_outp_check_file = f'{HOME}/subtaker/subprocessing-outputs/3_cs2-outp(to-test-if-ok)DEL-AFTER/{ftimestamp}-dnsgen'


        # 6. Massdns step #5 ################################################################## 6
        #! enhancement: create function for MassDNS resolution (same as 4.1)
        
        time_now = str(datetime.now().strftime('%H:%M'))
        print(f'{time_now} > starting MassDNS on {len(dnsgen_outp_list):,d} possible subdomains from DNSGEN')
        print(f'{time_now} > output will be saved as .ndjson file')

        massdns_count_5 = len(dnsgen_outp_list)
       
        NDJ_OUTP_5 = f'{HOME}/subtaker/subprocessing-outputs/4_6_massdns_ndjson-outp/{ftimestamp}_5_{company_name}.ndjson'

        massdns_5_time_start = datetime.now()


        massdns_sliced_list(dnsgen_outp_list, NDJ_OUTP_5) # massdns resolution in sliced parts
        

        massdns_5_time_end = datetime.now()
    
        massdns_5_time_total_sec = int((massdns_5_time_end - massdns_5_time_start).total_seconds())
        
        #! Error if skipping anything
        massdns_time_total_sec = massdns_1_time_total_sec + massdns_2_time_total_sec + massdns_3_time_total_sec + massdns_5_time_total_sec

        #! Error if skipping anything
        massdns_count_total = massdns_count_1 + massdns_count_2 + massdns_count_3 + massdns_count_5

        # Avoiding division by zero error
        if massdns_time_total_sec == 0:
            massdns_time_total_sec = 1

        massdns_time_total_min = massdns_time_total_sec / 60

        massdns_res_rate_sec = massdns_count_total / massdns_time_total_sec
        massdns_res_rate_min = massdns_count_total / massdns_time_total_min

        all_massdns_res_rate_sec = int(massdns_res_rate_sec)
        all_massdns_res_rate_min = int(massdns_res_rate_min)
        print(colored(f'      > massdns resolution rate = {all_massdns_res_rate_sec:,d} / second', 'green'))
        print(colored(f'                                = {all_massdns_res_rate_min:,d} / minute', 'green'))

        with open(NDJ_OUTP_5, 'r') as ndj:
            ndj_line_count = 0
            cname_count = 0
            for line in ndj:
                ndj_line_count += 1
                if 'CNAME' in line:
                    cname_count += 1

        print()
        time_now = str(datetime.now().strftime('%H:%M'))
        print(f'{time_now} > MassDNS finished on DSNGEN output:')
        print(colored(f'      > {ndj_line_count:,d} total records retrieved', 'yellow'))
        print(colored(f'      > {cname_count:,d} CNAME records retrieved', 'yellow'))

        print('\n-------------------------------------------\n')



    # 7. Merging .ndjson from steps #1 #2 #3 and #5
    # + Generating subdomains file for Nuclei
    
    time_now = str(datetime.now().strftime('%H:%M'))
    print(f'{time_now} > parsing generated .ndjson file(s) and merging them to serve as input for Nuclei\n')

    input_for_httpx_file = f'{HOME}/subtaker/subprocessing-outputs/7_a_inputs-for-httpx/{ftimestamp}-{company_name}-input_for_httpx.txt'

    #! enhancement: make function
    # each cname on this list will be verified if already in company all discovered cnames
    # if cname not already in file (that is, if really new) then it is appended to file
    cnames_all_found_list = []

    del p
    p = subprocess.run([f'grep CNAME {NDJ_OUTP_1}\
        | jq -crM \'.data | .answers | .[] | if .type == "CNAME" then .name else empty end\'\
        | sort\
        | uniq'],
        shell=True, capture_output=True, text=True)

    if p.stdout:
        cnames_all_found_list.extend(p.stdout.split('\n'))
        with open(input_for_httpx_file, 'a') as f:
            f.write(p.stdout) # no need for "f.write('\n')" anywhere (TESTED!)

    del p
    p = subprocess.run([f'grep CNAME {NDJ_OUTP_2}\
        | jq -crM \'.data | .answers | .[] | if .type == "CNAME" then .name else empty end\'\
        | sort\
        | uniq'],
        shell=True, capture_output=True, text=True)

    if p.stdout:
        cnames_all_found_list.extend(p.stdout.split('\n'))
        with open(input_for_httpx_file, 'a') as f:
            f.write(p.stdout) # no need for "f.write('\n')" anywhere (TESTED!)

    del p
    p = subprocess.run([f'grep CNAME {NDJ_OUTP_3}\
        | jq -crM \'.data | .answers | .[] | if .type == "CNAME" then .name else empty end\'\
        | sort\
        | uniq'],
        shell=True, capture_output=True, text=True)

    cnames_bruteforced_list = [] #! working on:

    if p.stdout:
        cnames_bruteforced_list += [cname for cname in p.stdout.split('\n') if cname not in cnames_all_found_list]
        cnames_all_found_list.extend(p.stdout.split('\n'))
        with open(input_for_httpx_file, 'a') as f:
            f.write(p.stdout) # no need for "f.write('\n')" anywhere (TESTED!)

    del p
    p = subprocess.run([f'grep CNAME {NDJ_OUTP_5}\
        | jq -crM \'.data | .answers | .[] | if .type == "CNAME" then .name else empty end\'\
        | sort\
        | uniq'],
        shell=True, capture_output=True, text=True)

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