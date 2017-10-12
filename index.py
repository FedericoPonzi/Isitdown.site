from flask import Flask, render_template, request, send_file, Markup, json, jsonify, send_from_directory, Blueprint
from socket import gaierror
import os
import subprocess
import requests
from urllib3.exceptions import ReadTimeoutError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import and_
from sqlalchemy import desc

from datetime import datetime, timedelta

#from sqlalchemy.dialects import postgresql
db = SQLAlchemy()

def create_app(DATABASE_URI):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.register_blueprint(bp)
    db.init_app(app)
    #db.create_all()
    return app

bp = Blueprint('index', __name__, static_folder="/static", template_folder="templates")

@bp.route("/api/<string:host>")
def jsonCheck(host=""):
    return jsonify(isitdown=doPing(host))

#Some static files:
@bp.route("/favicon.ico")
@bp.route("/robots.txt")
@bp.route("/sitemap.xml")
@bp.route("/humans.txt")
def getRobots():
    return send_from_directory(bp.static_folder, request.path[1:])

@bp.route("/")
@bp.route("/<string:host>")
def check(host=""):
    res = Pings.getLastPings()
    if len(host) == 0:
        return render_template("index.html", last=res)
    return render_template("check.html", pingres=Pings.isLastPingSuccessfull(host) or doPing(host), host=host, last=res)

@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404



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

    @classmethod
    def getLastPings(n=10):
        p = db.session.query(Pings.t, Pings.down, db.func.max(Pings.id).label("id")).order_by(desc("id")).group_by(Pings.t, Pings.down).limit(10)
        return p.all()

    def isLastPingSuccessfull(host):
        """
            Caches/limit requests to down sites to 1 per minute.
            Returns
            ------
            True, if the host was reported as up in the last minute
            False, otherwise.
        """
        oneMinuteAgo = datetime.utcnow() - timedelta(minutes=1)
        last = Pings.query.filter(and_(Pings.t == host, oneMinuteAgo < Pings.at )).all()
        return len(last) > 0 and last[0].down

    def __repr__(self):
        return 'Pings(id=%r, from= %r, to= %r, at=%r, down=%r)' % (self.id, self.f, self.t, self.at, self.down)


def doPing(host):
    '''@Return true, if host is down. False otherwise'''
    httpHost = "http://" + host
    print("Requested " + httpHost)
    isDown = True
    try:
        resp = requests.head(httpHost, timeout=2) #Every response is good :)
        isDown = False
    except Exception as e:
        if "Name or service not known" in repr(e):
            return True
        print(repr(e))
    p = Pings(request.access_route[-1],  Markup(host), datetime.utcnow(), isDown)
    db.session.add(p)
    db.session.commit()
    return isDown


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = create_app(DATABASE_URI = os.environ["DATABASE_URL"])
    app.run(host='0.0.0.0', port=port)
