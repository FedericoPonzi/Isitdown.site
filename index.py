from flask import Flask, render_template, request, send_file
import os
import subprocess
import requests
from urllib3.exceptions import ReadTimeoutError
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)

class Pings(db.Model):
    __tablename__ = "pings"
    id = db.Column(db.Integer, primary_key=True)
    f = db.Column(db.String(120)) # from
    t = db.Column(db.String(120)) # to
    at = db.Column(db.DateTime) # at

    def __init__(self, f, t, at):
        self.f = f
        self.t = t
        self.at = at

    def __repr__(self):
        return '<from: %r, to: %r, at: %r>' % (self.f, self.t, self.at)

@app.route("/")
@app.route("/<string:host>")
def check(host=""):
    res = Pings.query.order_by(Pings.at.desc()).limit(5).all()
    print(res)
    if len(host) == 0:
        return render_template("index.html")
    return render_template("check.html", pingres=doPing(host), host=host)

@app.route("/favicon.ico")
def favicon():
     return send_file("static/img/favicon.ico", mimetype='image/ico')
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

def doPing(host):
    host = host if host[:7] == "http://" else "http://" + host
    print("Request " + host)
    res = "up."
    try:
        resp = requests.head(host, timeout=2) #Every response is good :)
    except ReadTimeoutError as e:
        res="down."
    except Exception as e:
        # Host not found, and other
        print(repr(e))
        res="down."
    p = Pings(request.remote_addr, host, datetime.datetime.utcnow())
    db.session.add(p)
    db.session.commit()
    return res
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    db.create_all()
    app.run(host='0.0.0.0', port=port)
