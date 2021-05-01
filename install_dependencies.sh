#!/bin/bash

sudo apt update
sudo apt install python3-pip -y #pip3

pip3 install ndjson
pip3 install more-itertools
pip3 install jq

echo " ______________________"
echo "|      IMPORTANT!      |"
echo " ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾"
echo "[!] Make sure you have the following programs installed:"
echo ""
echo "  Amass by OWASP"
echo "  Massdns by Blechschmidt"
echo "  Nuclei by Project Discovery"
echo ""
echo "[!] You also need to make command aliases, or add the following programs to the '\$PATH' environment variable:"
echo ""
echo "  massdns"
echo "  nuclei"
echo ""
