import datetime
import os
from datetime import datetime

import requests
from flask import Flask, render_template, request, Markup, jsonify, send_from_directory, Blueprint
from flask_sqlalchemy import SQLAlchemy

from pings import Pings, PingsRepository

#from sqlalchemy.dialects import postgresql
db = SQLAlchemy()


def create_app(DATABASE_URI):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.register_blueprint(bp)
    db.init_app(app)
    return app


bp = Blueprint('index', __name__, static_folder="static", template_folder="templates")


@bp.route("/api/<string:host>")
def jsonCheck(host=""):
    return jsonify(isitdown=doPing(host))


# Some static files:
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
    httpHost = "https://" + host
    app.logger.info("Requested " + httpHost)
    isDown = True
    try:
        resp = requests.head(httpHost, timeout=2) #Every response is good :)
        app.logger.info(resp.status_code)
        # If we come here, we had a response. So the site is not down:
        isDown = False
    except Exception as e:
        app.logger.info(e)
        if "Name or service not known" in repr(e):
            return True

    p = Pings(request.access_route[-1],  Markup(host), datetime.utcnow(), isDown, resp.status_code)
    PingsRepository.addPing(p)
    return isDown


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = create_app(DATABASE_URI = os.environ["DATABASE_URI"])
    app.run(host='0.0.0.0', port=port)
