# Subtaker
A Subdomain Takeover Hunter


# Legal Warning
Do not use this tool on websites you don't have permission.


# Disclaimer 
At the time of the inital commit, the code lacks many good practices and it's also not fully optimized performance-wise.

I created this project as a mean to learn python, not worrying about good coding practices at the time. Although I know good practices are a MUST, I tried to get this program running quickly to potentially find vulnerabilities on Bug Bounty Programs ASAP. Also, bear in mind that I didn't have the initial intention to make this project public, so it doesn't have much of a user-friendly installation process, the code also contains many comments to myself that may not make sense to you.

I may eventually make the code cleaner from time to time. It just so happens not to be my life priority right now. Time is valuable, use it wisely! :)

Feel free to branch and push request it with cleaner code, good practices, and optimizations. They are welcome!


# About Subtaker
This is a tool to find Subdomain Takeover vulnerabilities.

I developed this tool with the primary objective to learn python. Making a functional tool capable of neatly finding vulnerabilities were always in second plan. Also, I thought this project was going to be shorter so I didn't worry about modules, classes or anything. It's also not so user friendly to install and use because initially I didn't have the intention to make this repository public, so you have been warned! :)

If you want to go deeper into the rabbit hole on how it works, you should check Patrik Hudák's (0xpatrik) [blog] and [Master's Thesis]. Most of the principles applied to this project were based on his content (big thanks!).

[blog]: https://0xpatrik.com
[Master's Thesis]: https://is.muni.cz/th/byrdn/Thesis.pdf


# How to Use It
First, you need to install/do all the [Requirements].

Before you run the script, you should create a ".txt" file listing the main (sub)domains described in the scope of the bug bounty program of your target. 

Inside the .txt list you should have something like:
```
example.com
sub.example.com
example.net
```
> Plain and simple. No "http://". No "https://". No "\*.something.com", just "something.com", "sub.something.com" (without the quotes).

Then, place the .txt file in the folder:
```
/home/your_username/subtaker/inscopes/to-check
```

I recommend creating multiple files for different companies. You can place all of them in the "to-check" folder. Subtaker will run the script on each file at a time.

Then, run the script with Python 3:
```
python3 /home/your_username/subtaker.py
```

[Requirements]: https://github.com/it-jhack/subtaker#requirements


Subtaker will:
- Bruteforce using your wordlist to be set previously.
- Automatically send the txt list file from ```to-check``` to ```done``` folder after the scan is finished.
- Register your scan details at log-inscopes.csv. I use tabview to quickly check it on terminal.
- Create lists on the "subprocessing-outputs" folder with the results obtained from Amass, FDNS CNAME parsing, MassDNS, and Nuclei.
- Print on the terminal, create a report, and notify you on your email should it find any potential vulnerability.

# Important Notice

This project was developed and tested on Ubuntu and Kali Linux.

You need to clone Subtaker at:
```
/home/your_username/
```


# Requirements

It's recommended that you update the system to the latest packages before beginning any major installations (this may take a while):
```
sudo apt-get update && sudo apt-get upgrade
```

## Rapid7's FDNS CNAME file

Save the latest [Rapid7's FDNS CNAME file] in the folder (it has a few Gigabytes):
```
/home/your_username/subtaker/fdns
```
> Do NOT decompress the file

Always check for updates. You need to register (for free) to have access to the most recent files. Otherwise, by using old files you may get less accurate results and more false-positives.

[Rapid7's FDNS CNAME file]: https://opendata.rapid7.com/sonar.fdns_v2

## Bruteforce Wordlist of Your Choice

You will need 3 different wordlists in order to bruteforce subdomains:
- Slow - Save it as "wordlist.txt"
- Fast - Save it as "fast_wordlist.txt"
- Super Fast - Save it as "superfast_wordlist.txt"

For that purpose I recommend the [Commonspeak2] wordlist top 500k, 20k, and 200 words, respectively.

Paste all of the files in the "/subtaker/wordlists/" folder:

If you don't create all three wordlists you should skip bruteforcing, otherwise the scan will fail.

[Commonspeak2]: https://github.com/assetnote/commonspeak2-wordlists

## Python 3
You need to execute the script with python 3. To check if you have it installed:
```
python3 --version
```

To install python 3:
```
sudo apt install python3
```
Or
```
sudo apt-get install python3
```


## pip3
```
sudo apt install python3-pip
pip3 --version
```

## python3 requests package
```
sudo pip3 install requests
```

## python3 ndjson
```
sudo pip3 install ndjson
```

## MassDNS (by blechschmidt)
```
cd /home/your_username/
git clone https://github.com/blechschmidt/massdns.git
```
You'll need to create a command alias as explained further


## Golang
- Go to https://golang.org/
- Download the latest version for Linux. Also pick your correct processor architecture, ex.:
“goX.XX.X.linux-amd64.tar.gz”
- Open your terminal where you downloaded the file and substitute the name of the file on the following command:
	```tar -C /usr/local -xfz goX.XX.X.linux-amd64.tar.gz```
- Default installation path is: /home/your_username/go

You may need to change Golang's default path. Open the terminal and edit the environment variables file. On Ubuntu and Kali Linux it's the .bashrc:
```
nano /home/your_username/.bashrc
```
Then, paste this line at the end of the file:
```bash
export PATH=$PATH:/usr/local/go/bin
```
If you cannot install golang, you may try this alternate [tutorial].

[tutorial]: https://tzusec.com/how-to-install-golang-in-kali-linux/

If you still encounter any error, you'll need to refer to an updated official golang documentation or follow some other tutorial online.

To check if you have installed Golang successfully, type on the terminal:
```
go version
```

## Amass (OWASP)
```
sudo apt-get install amass
```

## JQ
```
sudo apt-get install jq
```

## Nuclei (by projectdiscovery)
```
cd /home/your_username/
git clone https://github.com/projectdiscovery/nuclei.git
cd nuclei/v2/cmd/nuclei/
go build
mv nuclei /usr/local/bin/
nuclei -version
```

## Create Environment Variables

Use a text editor to edit you environment variables file. On Ubuntu and Kali Linux it's the .bashrc, example:
```
nano /home/your_username/.bashrc
```

You need to create environment variables using an email of your choice (I used gmail). This way you'll get an email notification when subtaker finds a potential vulnerability.

Note, this is not your "true" gmail password that you're going to be using. It's only a "secondary password" with limited scope.

Create an app password at https://myaccount.google.com/apppasswords

Then add the following lines to the end of the file:
```bash
export EMAIL_USER="example@gmail.com"
```
> Change the example to your sender email. Do not delete the quotation marks.

```bash
export EMAIL_APP_PASS="your_gmail_app_password"
```
> Paste your app password here.

```bash
export EMAIL_RECEIVER="your_notification_email@example.com"
```
> This is the address that will receive the notifications. It could be any email, preferrably the one you have logged in on your phone.

Then you need to save and exit. To save on Nano text editor:
```
Ctrl + O
Enter
```

To close:
```
Ctrl + X
```

Finally, you need to close the terminal and open it again.

## Create Aliases
Use a text editor to create or edit you aliases file. On Ubuntu and Kali Linux it's the .bash_aliases, example:
```
nano /home/your_username/.bash_aliases
```

Make an alias for MassDNS using the path it's installed, example:
```bash
alias massdns='/home/your_username/massdns/bin/massdns'
```

Finally, you need to close the terminal and open it again.

After this, you should be all set to [run Subtaker].

[run subtaker]: https://github.com/it-jhack/subtaker#how-to-use-it
