import sys
import datetime
import os
from datetime import datetime
import logging
import requests
from flask import Flask, render_template, request, Markup, jsonify, send_from_directory, Blueprint
from flask_sqlalchemy import SQLAlchemy

from pings import Pings, PingsRepository


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
    lastPingList = PingsRepository.getLastPings()
    if len(host) == 0:
        return render_template("index.html", last=lastPingList)
    return render_template("check.html", pingres=PingsRepository.isLastPingSuccessfull(host) or doPing(host), host=host, last=lastPingList)


@bp.errorhandler(404)
def page_not_found(error):
    app.log_exception(error)
    return render_template('404.html'), 404


def doPing(host, prefix="https://"):
    '''
    @:returns true, if host is down
    '''
    httpHost = prefix + host
    isDown = True
    response_code = -1
    logger.debug("Sending head request to:" + httpHost)

    try:
        resp = requests.head(httpHost, timeout=2, stream=True, allow_redirects=True)
        app.logger.debug(resp.status_code)
        # If we come here, we had a response. So the site is up:
        isDown = False
        response_code = resp.status_code
    except Exception as e:
        if "Name or service not known" in repr(e):
            return True
        logger.error("Exception while contacting {}. Exception: {} ".format(host, e))

        # Check both https and http:
        if "Connection refused" in repr(e):
            return doPing(host, "http://")

    p = Pings(request.access_route[-1],  Markup(host), datetime.utcnow(), isDown, response_code)
    PingsRepository.addPing(p)
    return isDown


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger = logging.getLogger('isitdown_app')
    logger.setLevel(logging.ERROR)
    if os.environ.get("FLASK_ENV", "development") == "development":
        logger.setLevel(logging.DEBUG)

    app = create_app(DATABASE_URI = os.environ["DATABASE_URI"])
    app.run(host='0.0.0.0', port=port)
