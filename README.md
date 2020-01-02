# Isitdown.site
[![Build Status](https://travis-ci.org/FedericoPonzi/Isitdown.site.svg?branch=master)](https://travis-ci.org/FedericoPonzi/Isitdown.site)
[![codecov](https://codecov.io/gh/FedericoPonzi/Isitdown.site/branch/master/graph/badge.svg)](https://codecov.io/gh/FedericoPonzi/Isitdown.site)

This is the source code for [isitdown.site](http://isitdown.site)

It's made with: 
 * Flask (python3.5), 
 * PostgreSQL, 
 * HTML5/CSS (with HTML5 boilerplate)
 * Was hosted on Heroku (<3 for them) but now it's hosted on Linode (<3 for 
    them too)

> Please note: The logo is handmade by
[Antonio Di Rosso](https://www.behance.net/nano88) so you should *not* use it in other projects.

## Development
 * Required `PostreSQL` (or at least `SQLite`) and `Python >= 3.5` installed.
 * create a user and a database for `isitdown.site`
 * give `build.sh` run permissions: `chmod +x build.sh`
 * run `./build.sh` to create the virtual environment and download the required packages.
 * use `source .venv/bin/activate` to activate the virtual environment
 * Add the database connection uri as environment variable: `export ISITDOWN_DATABASE_URI=postgresql://username:password@localhost/database`. You can also use `ISITDOWN_PORT` variable to override the default listening port (`5000`).
 * use `FLASK_APP=isitdown.dex.py flask run` to run the site.
 * use `python -m pytest` to run tests.

## Deployment
I've attached `flask.wsgi.template` used to install it within apache web server.

## Environment
 * `ISITDOWN_DATABASE_URI`: The database connection string.
 * `ISITDOWN_PORT`: The port to listen on
 * `FLASK_ENV`: With `development`, it will print useful debug messages.

## License
Please check the [LICENSE](LICENSE) file.
