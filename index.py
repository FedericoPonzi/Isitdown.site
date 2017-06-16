from flask import Flask, render_template
import os
import subprocess
from ping import ping
app = Flask(__name__)

@app.route("/")
@app.route("/<string:host>")
def check(host=""):
    if len(host) == 0:
        return render_template("index.html")
    return render_template("check.html", pingres=doPing(host), host=host)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

def doPing(host):
    ipaddress = host # guess who
    if requests.head(ipaddress).status_code == 200:
        return "up."
    else:
        return "down."
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
