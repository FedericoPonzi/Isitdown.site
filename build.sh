#!/bin/sh
set -e
pip3 install virtualenv
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt
deactivate
