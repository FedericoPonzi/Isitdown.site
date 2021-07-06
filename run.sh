#!/bin/sh
source venv/bin/activate
# Setup the db:
FLASK_APP=isitdown.index flask db upgrade
# Run the website
#python3 -m isitdown.index
waitress-serve --listen=*:8080 --call 'isitdown.index:create_app'
