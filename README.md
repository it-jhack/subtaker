![screenshot](https://github.com/it-jhack/subtaker/blob/main/.img/screenshot.png)


## Legal Warning
Do not use this tool on assets you don't have permission! Proceed at your own responsibility.


## Disclaimer 
I created this project with the objective to learn python, OO, networking, and ethical hacking, simultaneously.

Feel free to branch and do push requests with improvements as you see fit. They are a great opportunity for me to learn so they're very welcome.

A shout out to Patrik Hudák, as this project had many networking concepts and code snippets based from his [website] and [master's thesis].

[website]: https://0xpatrik.com
[Master's Thesis]: https://is.muni.cz/th/byrdn/Thesis.pdf


## About Subtaker
Subtaker is a tool to find Subdomain Takeover vulnerabilities.

Provided all options, Subtaker will:

- Run `amass enum --passive -d <domain>` to enumerate subdomains for each (sub)domain in -f file.
- Grep `fdns_cname.json.gz` for extra subdomains discovery.
- Bruteforce each (sub)domain in -f with the provided wordlist.
- Resolve subdomains using Massdns with 15,000 concurrent DNS lookups.
- Generate a `.ndjson` report file at `--out-dir` path with detailed subdomain resolutions. A `.txt` file containing only subdomains will also be generated.
- Run nuclei 'takeover' scripts on resolved subdomains.
- If there is any possible takeover, nuclei will create a 'possible-takeovers' report file.

> Each report file will be prefixed with the time of subtaker execution in the format: `yymmdd-hhmmss-`


## What is Subdomain Takeover?
In a nutshell, a subdomain takeover (as the name may suggest) is when an attacker takes control over an expired subdomain. So, for example, Company Inc. has a website up and running called 'company.com'. An attacker is able to take control over a forgotten expired subdomain called 'help.store.company.com'. So now he may maliciously trick unsuspecting Company's customers into providing user credentials, credit cards, etc.

If you want to learn about it in more detail, I recommend getting started at [this] and [this post]. If you want to go deeper into the rabbit hole on how it works, you should check Patrik Hudák's (0xpatrik) posts and Master's Thesis mentioned above.

[this]: https://0xpatrik.com/subdomain-takeover-basics/
[this post]: https://www.hackerone.com/blog/Guide-Subdomain-Takeovers


## Installation

```
git clone https://github.com/it-jhack/subtaker.git
cd subtaker
./install-py-packs.sh
```

## Pre Requirements
Subtaker was only tested on Debian Linux. To run subtaker, you need to have installed:

- Python 3
- Amass: by OWASP*
- Massdns: by Blechschmidt
- Nuclei: by Project Discovery

>*You also need to create a 'massdns' alias, or add its binary path to \$PATH environment variable

Example of making an alias for Massdns, on a Debian system:

```bash
echo "alias massdns=\"\$HOME/bugbounty/+tools/massdns/bin/massdns\"" >> $HOME/.bashrc
```
After entering the command above, you need to restart your console or enter `source .bashrc`


# How to Use It

| Argument      | Description                |
| ------------- | -------------------------- |
| -h, --help    | show help message and exit |
| -f <file> | List domains in a '.txt' file. Each domain must be in a different line. Do not include 'http://' or 'https://'. Usage: -f domains.txt |
| --out-dir <dir_path> | Directory base path to output report files. If not provided, default output dir will be same as 'pwd' command. Usage: --out-dir /path/to/dir/ |
| --amass-enum | Do subdomain enumeration with amass |
| --amass-config <config_file> | Path to Amass .ini configuration file. Usage: --amass-config /path/config.ini |
| --fdns <file.json.gz> | Path to the file containing Forward DNS data (do NOT extract the file). See 'opendata.rapid7.com'. Usage: --fdns cname_file.json.gz |
| --brute <file> | Bruteforce subdomains. Usage: --brute wordlist.txt |
| --concurrent <number> | Number of concurrent DNS lookups. Default is 10,000. Usage: --concurrent 5000|

Example using all options:
```bash
python3 subtaker.py -f path/main_domains.txt --out-dir /outp/dir/ --amass-enum --amass-config /path/config.ini --brute /path/wordlist.txt --concurrent 15000 --fdns /path/2021-05-08-1620432305-fdns_cname.json.gz
```

> Note that the -f file should contain domains, NOT urls.


## Features to Add

- Implement Rapid7's OpenData RDNS subdomain discovery;
- Massdns, Nuclei progress bar;
- Add all vulnerable/edge case fingerprints from [Can I Takeover XYZ] project

[Can I Takeover XYZ]: https://github.com/EdOverflow/can-i-take-over-xyz