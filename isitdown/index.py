import datetime
import os
import re
from datetime import datetime
import requests
from flask import Flask, render_template, request, Markup, jsonify, send_from_directory, Blueprint, current_app
from isitdown.repository import Pings, PingsRepository, db

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


@bp.route("/api/v2/<string:host>")
def jsonCheck(host=""):
    if not isValidHost(host):
        return jsonify(isitdown=False)
    p = PingsRepository.wasDownOneMinuteAgo(host)
    if p.isdown:
        p = doPing(host)
    return jsonify(isitdown=p.isdown, response_code=p.response_code)


# Some static files:
@bp.route("/favicon.ico")
@bp.route("/robots.txt")
@bp.route("/sitemap.xml")
@bp.route("/humans.txt")
def getRobots():
    return send_from_directory(bp.static_folder, request.path[1:])


def isValidHost(host):
    regex = r"((http:\/\/)|(https:\/\/)){0,1}([a-zA-Z0-9-]+\.)+([a-zA-Z])+"
    pattern = re.compile(regex)
    if not pattern.match(host):
        logger.error("Regex for site: " + host +" not passed.")
    return pattern.match(host)


@bp.route("/")
@bp.route("/<string:host>")
def check(host=""):
    lastPingList = PingsRepository.getLastPings()
    if len(host) == 0:
        return render_template("index.html", last=lastPingList)
    p = PingsRepository.wasDownOneMinuteAgo(host)
    if p.isdown:
        p = doPing(host)
    return render_template("check.html", last=lastPingList, pingres=p)


@bp.errorhandler(404)
def page_not_found(error):
    current_app.logger.error(error)
    return render_template('404.html'), 404

@bp.route("/users")
def users():
    return render_template('users/login.html')

def doPing(host, prefix="https://"):
    '''
    @:returns p, the result of the ping. It may return a boolean (True) if there are some validation errors.
    '''
    if not isValidHost(host):
        current_app.logger.debug("Error validating host.")
        return Pings(host= host, isdown=True)

    httpHost = prefix + host
    isDown = True
    response_code = -1
    current_app.logger.debug("Sending head request to:" + httpHost)
    headers = {
        'User-Agent': 'isitdown.site(Check if a site is down)',
    }
    try:
        resp = requests.head(httpHost, timeout=2, stream=True, allow_redirects=True, headers=headers)
        # If we come here, we had a response. So the site is up:
        isDown = False
        response_code = resp.status_code
    except Exception as e:
        if "Name or service not known" in repr(e): # TODO: Probably a more informative message would be better.
            return Pings(host=host, isdown=True)

        current_app.logger.error("Exception while contacting {}. Exception: {} ".format(host, e))

        # Check both https and http:
        if "Connection refused" in repr(e):
            return doPing(host, "http://")

    # ip_addr = socket.gethostbyname(host) uh-uh

    p = Pings(from_ip=request.access_route[-1], host=Markup(host),time_stamp=datetime.utcnow(), isdown=isDown,
              response_code=response_code)
    PingsRepository.addPing(p)
    return p


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    if "DATABASE_URI" not in os.environ:
        print("Fatal: missing DATABASE_URI environment variable.")
        import sys
        sys.exit(-1)
    app = create_app(DATABASE_URI=os.environ["DATABASE_URI"])
    logger = app.logger
    app.run(host='0.0.0.0', port=port)
