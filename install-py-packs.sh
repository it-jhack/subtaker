#!/bin/bash

sudo apt update
sudo apt install -y python3-pip #pip3

pip3 install ndjson
pip3 install more-itertools
pip3 install jq

echo ""
echo ""
echo " ______________________"
echo "|      IMPORTANT!      |"
echo " ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾"
echo "[!] Before running subtaker.py, make sure you have the following programs installed:"
echo ""
echo "    Amass by OWASP"
echo "    Massdns by Blechschmidt*"
echo "    Nuclei by Project Discovery"
echo ""
echo "    *You also need to create a 'massdns' alias, or add its binary path to \$PATH environment variable"
echo ""

echo "Example of a command making an alias for Massdns, on a Debian system:"
echo ""

# Paste this command on terminal: echo "alias massdns=\"\$HOME/massdns/bin/massdns\"" >> $HOME/.bashrc
echo "echo \"alias massdns=\\\"\\\$HOME/massdns/bin/massdns\\\"\" >> \$HOME/.bashrc"
echo ""
