import datetime
import os
from datetime import datetime
import requests
from flask import Flask, render_template, request, Markup, jsonify, send_from_directory, Blueprint, current_app
from flask_sqlalchemy import SQLAlchemy
from isitdown.repository import Pings, PingsRepository
from repository import db

logger = None


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return db


def create_app(DATABASE_URI=None):
    if type(DATABASE_URI) != str:
        print("Error: Database URI is:" + str(DATABASE_URI))
        return None
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = str(DATABASE_URI)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #app.config['SQLALCHEMY_ECHO'] = True
    db = init_db(app)
    app.register_blueprint(bp)

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
    logger.error(error)
    return render_template('404.html'), 404


def doPing(host, prefix="https://"):
    '''
    @:returns true, if host is down
    '''
    httpHost = prefix + host
    isDown = True
    response_code = -1
    current_app.logger.debug("Sending head request to:" + httpHost)

    try:
        resp = requests.head(httpHost, timeout=2, stream=True, allow_redirects=True)
        # If we come here, we had a response. So the site is up:
        isDown = False
        response_code = resp.status_code
    except Exception as e:
        if "Name or service not known" in repr(e):
            return True
        current_app.logger.error("Exception while contacting {}. Exception: {} ".format(host, e))

        # Check both https and http:
        if "Connection refused" in repr(e):
            return doPing(host, "http://")

    # ip_addr = socket.gethostbyname(host) uh-uh

    p = Pings(from_ip=request.access_route[-1], host=Markup(host),time_stamp=datetime.utcnow(), isdown=isDown, response_code=response_code)
    PingsRepository.addPing(p)
    return isDown


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    if "DATABASE_URI" not in os.environ:
        print("Error: missing DATABASE_URI environment variable.")
        import sys
        sys.exit(-1)
    app = create_app(DATABASE_URI=os.environ["DATABASE_URI"])
    logger = app.logger
    app.run(host='0.0.0.0', port=port)
