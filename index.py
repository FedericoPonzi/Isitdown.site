from flask import Flask, render_template, request, send_file, Markup, json, jsonify, send_from_directory, Blueprint
from socket import gaierror
import os
import subprocess
import requests
from urllib3.exceptions import ReadTimeoutError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import and_
from sqlalchemy import desc
import datetime
from pings import Pings, PingsRepository

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

bp = Blueprint('index', __name__, static_folder="static", template_folder="templates")

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
    res = PingsRepository.getLastPings()
    if len(host) == 0:
        return render_template("index.html", last=res)
    return render_template("check.html", pingres=PingsRepository.isLastPingSuccessfull(host) or doPing(host), host=host, last=res)

@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


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
    PingsRepository.addPing(p)
    return isDown


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = create_app(DATABASE_URI = os.environ["DATABASE_URL"])
    app.run(host='0.0.0.0', port=port)
