# Isitdown.site
[![Build Status](https://travis-ci.org/FedericoPonzi/Isitdown.site.svg?branch=master)](https://travis-ci.org/FedericoPonzi/Isitdown.site)
[![codecov](https://codecov.io/gh/FedericoPonzi/Isitdown.site/branch/master/graph/badge.svg)](https://codecov.io/gh/FedericoPonzi/Isitdown.site)

This is the source code for [isitdown.site](http://isitdown.site)

It's made with: 
 * Flask (python3), 
 * PostgreSQL, 
 * HTML5/CSS (with HTML5 boilerplate)
 * Was hosted on Heroku (<3 for them) but now it's hosted on Linode (<3 for 
    them too)

*Please note: The logo is handmade by
[Antonio Di Rosso](https://www.behance.net/nano88) so you should *not* use it in other projects.*

## Installation
 * You should have Postresql and Python 3.6 installed.
 * Create a user and a database for isitdown.site, and import the isitdown.db file.
 * Give build.sh run permissions: `chmod +x build.sh`
 * Open a terminal, and run `./build.sh` to create the virtual environment and download the required packages.
    * It also need yui-compressor used to minify the css.
 * Type `source .venv/bin/activate` to activate the virtual environment
 * Add the database connection uri as enviornment variable: `export DATABASE_URI=postgresql://username:password@localhost/database`. You can add a `PORT` variable to ovverride the default listening port (5000).
 * Finally, run `python3 index.py` to run the site.

There is also a flask.wsgi.template used to install it in apache.

## Environment
 * `DATABASE_URI`: The database connection string.
 * `PORT`: The port to listen on
 * `FLASK_ENV`: With `development`, it will print useful debug messages.

## License
Please check the LICENSE file.
