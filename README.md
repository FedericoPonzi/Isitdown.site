# Isitdown.site
This is the source code for [isitdown.site](http://isitdown.site)

It's made with: 
 * Flask (python), 
 * PostgreSQL (just to store the requests), 
 * HTML5/CSS (with HTML5 boilerplate)
 * Was hosted on Heroku (<3 for them) but now it's hosted on Linode (<3 for 
    them too)

*Please note: The logo is handmade thanks to 
[Antonio Di Rosso](https://www.behance.net/nano88) 
(check his profile!) so you should *not* use it in other projects.*

## Installation
 * You should have Postresql and Python 3.6 installed.
 * Create a user and a database for isitdown.site, and import the isitdown.db file.
 * Give build.sh run permissions: `chmod +x build.sh`
 * Open a terminal, and run `./build.sh` to create the virtual environment and download the packets.
 * Type `source .venv/bin/activate` to activate the virtual environment
 * Add the database connection uri as enviornment variable: `export DATABASE_URL=postgresql://username:password@localhost/database`. You can add a `PORT` variable to ovverride the default listening port (5000).
 * Finally, run `python3 index.py` to run the site.

## License
Please check LICENSE file.
