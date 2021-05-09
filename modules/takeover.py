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
    return nuclei_p.stdout