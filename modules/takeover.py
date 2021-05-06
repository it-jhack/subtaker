import subprocess
import utils.cat_file


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
    nuclei_cmd = [
        'nuclei',
        '-t', 'takeovers',
        '-no-color',
        '-o', output_path,
        '-r', resolvers,
        '-rate-limit', 150,
        'silent',
    ]

    httprobe_urls = get_httprobe(subdomains_file)
    nuclei_p = subprocess.run(nuclei_cmd, capture_output=True, input=httprobe_urls)

    return nuclei_p.stdout
