from datetime import datetime

def get_time_hhmm():
    return datetime.now().strftime('%H:%M')

def get_time_yymmdd_hhmm():
    return datetime.now().strftime('%y%m%d-%H%M')

def screen_msg(message):
    print(f'{get_time_hhmm()} {message}')

def exec_and_readlines(cmd, domains):
    domains_str = bytes('\n'.join(domains), 'ascii')
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)
    stdout, stderr = proc.communicate(input=domains_str)

    return [j.decode('utf-8').strip() for j in stdout.splitlines() if j != b'\n']