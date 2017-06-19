from flask import Flask, render_template, request, send_file, Markup
from socket import gaierror
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
    down = db.Column(db.Boolean) # is it down?

    def __init__(self, f, t, at, d):
        self.f = f
        self.t = t
        self.at = at
        self.down = d

    def __repr__(self):
        return 'Pings(id=%r, from= %r, to= %r, at=%r, down=%r)' % (self.id, self.f, self.t, self.at, self.down)

from sqlalchemy.dialects import postgresql

@app.route("/")
@app.route("/<string:host>")
def check(host=""):
    # there must be a better way, "for the moment" this works:
    q = Pings.query.order_by(Pings.at.desc()).from_self().distinct(Pings.t).limit(10).from_self().order_by(Pings.at.desc())
    print (str(q.statement.compile(dialect=postgresql.dialect())))
    res = q.all()
    last = [x.t for x in res]
    if len(host) == 0:
        return render_template("index.html", last=res)
    return render_template("check.html", pingres=doPing(host), host=host, last=res)

@app.route("/favicon.ico")
def favicon():
     return send_file("static/img/favicon.ico", mimetype='image/ico')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

def doPing(host):
    httpHost = "http://" + host
    print("Requested " + httpHost)
    res = "down"
    down = True
    try:
        resp = requests.head(httpHost, timeout=2) #Every response is good :)
        res = "up"
        down = False
    except gaierror as e:
        # Name or service not found. Not gonna save it in the db
        return res
    except Exception as e:
        # Host not found, and other
        print(repr(e))

        if "service not known" in repr(e):
            print(res)
            return res

    p = Pings(request.remote_addr,  Markup(host), datetime.datetime.utcnow(), down)
    db.session.add(p)
    db.session.commit()
    return res
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    db.create_all()
    app.run(host='0.0.0.0', port=port)
