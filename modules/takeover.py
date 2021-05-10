import subprocess


def cat_file(file_path):
    cat_p = subprocess.run(['cat', file_path],
        capture_output=True)

    return cat_p.stdout


def get_httprobe(subdomains_file):
    cat_out = cat_file(subdomains_file)

    httprobe_p = subprocess.run(['httprobe'],
        capture_output=True, input=cat_out)

    return httprobe_p.stdout


def update_nuclei_templates():
    nuclei_upd = ['nuclei', '-update-templates']

    p = subprocess.run(nuclei_upd)


def get_nuclei(subdomains_file, output_path, resolvers):
    
    httprobe_urls = get_httprobe(subdomains_file)
    #!TODO BEGIN DEL TEST
    from datetime import datetime
    base_dir = f'/tmp/'
    ftimestamp = datetime.now().strftime('%y%m%d-%H%M%S')
    test_file = f'{base_dir}{ftimestamp}-test_takeover-get_httprobe-httprobe_urls-write'
    to_write = str(httprobe_urls)
    with open(test_file, 'w') as f:
        f.write(to_write)
    #!TODO END DEL TEST

    nuclei_cmd = [
        'nuclei',
        '-t', 'takeovers',
        '-no-color',
        '-o', output_path, # writes file
        '-r', resolvers,
        '-rate-limit', '150', # default = 150
        '-silent',
    ]
    
    nuclei_p = subprocess.run(nuclei_cmd, capture_output=True, input=httprobe_urls)

    # Already writes file (-o cmd option)
    # returning stdout in case of print() intended
    #!TODO BEGIN DEL TEST
    from datetime import datetime
    base_dir = f'/tmp/'
    ftimestamp = datetime.now().strftime('%y%m%d-%H%M%S')
    test_file = f'{base_dir}{ftimestamp}-test_get_nuclei-nuclei_p_stdout-theres_also_-o_arg_file_to_see-write'
    with open(test_file, 'w') as f:
        f.write(str(nuclei_p.stdout))
    #!TODO END DEL TEST
    return nuclei_p.stdout