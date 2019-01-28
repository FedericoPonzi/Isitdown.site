import datetime
import re
from datetime import datetime

import requests
from flask import render_template, request, Markup, jsonify, send_from_directory, Blueprint, current_app

from isitdown.repository import Pings, PingsRepository

frontend_bp = Blueprint('index', __name__, static_folder="static", template_folder="templates")


@frontend_bp.route("/api/v2/<string:host>")
def json_check(host=""):
    if not is_valid_host(host):
        return jsonify(isitdown=False)
    p = PingsRepository.wasDownOneMinuteAgo(host)
    if p.isdown:
        p = do_ping(host)
    return jsonify(isitdown=p.isdown, response_code=p.response_code)


# Some static files:
@frontend_bp.route("/favicon.ico")
@frontend_bp.route("/robots.txt")
@frontend_bp.route("/sitemap.xml")
@frontend_bp.route("/humans.txt")
def get_robots():
    return send_from_directory(frontend_bp.static_folder, request.path[1:])


def is_valid_host(host):
    regex = r"((http:\/\/)|(https:\/\/)){0,1}([a-zA-Z0-9-]+\.)+([a-zA-Z])+"
    pattern = re.compile(regex)
    if not pattern.match(host):
        current_app.logger.error("Regex for site: " + host +" not passed.")
    return pattern.match(host)


@frontend_bp.route("/")
@frontend_bp.route("/<string:host>")
def check(host=""):
    lastPingList = PingsRepository.getLastPings()
    if len(host) == 0:
        return render_template("index.html", last=lastPingList)
    p = PingsRepository.wasDownOneMinuteAgo(host)
    if p.isdown:
        p = do_ping(host)
    return render_template("check.html", last=lastPingList, pingres=p)


@frontend_bp.errorhandler(404)
def page_not_found(error):
    current_app.logger.error(error)
    return render_template('404.html'), 404


def do_ping(host, prefix="https://"):
    '''
    @:returns p, the result of the ping. It may return a boolean (True) if there are some validation errors.
    '''
    if not is_valid_host(host):
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
            return do_ping(host, "http://")

    # ip_addr = socket.gethostbyname(host) uh-uh

    p = Pings(from_ip=request.access_route[-1], host=Markup(host),time_stamp=datetime.utcnow(), isdown=isDown,
              response_code=response_code)
    PingsRepository.addPing(p)
    return p
