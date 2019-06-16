import datetime
import re
from datetime import datetime

import requests
from flask import render_template, request, Markup, jsonify, send_from_directory, Blueprint, current_app

from isitdown.repository import Ping, PingRepository
import os

basedir = os.path.abspath(os.path.dirname(__file__))

frontend_bp = Blueprint('index', __name__, static_folder=os.path.join(basedir, "static"), template_folder="templates")
spam_list = [line.rstrip('\n') for line in open(os.path.dirname(os.path.abspath(__file__)) + '/res/spam.csv')]


@frontend_bp.route("/api/v3/<string:host>")
def apiv3(host=""):
    if not is_valid_host(host):
        return jsonify(isitdown=False)
    # 1. We return all the pings to this host in the last 30 seconds.
    # 2. if there is a from_ip in the list, return an error.
    pings = PingRepository.last_ping_to(host, current_app.config['BACKOFF_API_CALL_TIME'])
    for p in pings:
        if p.from_ip == request.access_route[-1]:
            return jsonify(error="Too many requests to the same site."), 429
    if len(pings) > 0:
        return jsonify(isitdown=pings[-1].isdown, response_code=p.response_code, host=host, deprecated=False)
    # If there isn't any ping in the last 30 seconds:
    ping = do_ping(host, from_api=3)
    return jsonify(isitdown=ping.isdown, response_code=ping.response_code, host=host, deprecated=False)


# Some static files:
@frontend_bp.route("/favicon.ico")
@frontend_bp.route("/robots.txt")
@frontend_bp.route("/sitemap.xml")
@frontend_bp.route("/humans.txt")
def get_robots():
    return send_from_directory(frontend_bp.static_folder, request.path[1:])


def is_valid_host(host):
    regex = r"((http:\/\/)|(https:\/\/)){0,1}([a-zA-Z0-9-]+\.)+([a-zA-Z])+"
    res = re.compile(regex).match(host)
    if not res:
        current_app.logger.error("Regex for site: {} not passed.".format(host))
    return res


@frontend_bp.route("/")
@frontend_bp.route("/<string:host>")
def check(host=""):
    last_ping_list = PingRepository.get_last_pings(request_source=0)
    if len(host) == 0:
        return render_template("index.html", last=last_ping_list)
    ping = PingRepository.was_down_one_minute_ago(host)
    if ping.isdown:
        ping = do_ping(host)
    return render_template("check.html", last=last_ping_list, pingres=ping)


@frontend_bp.errorhandler(404)
def page_not_found(error):
    current_app.logger.error(error)
    return render_template('404.html'), 404


def is_spam(host, spam=spam_list):
    return len(list(filter(lambda x: host in x, spam))) > 0


def do_ping(host, prefix="https://", from_api=0):
    '''
    @:returns a Ping(), with the result of the ping. It may or may not have been saved on the database.
    '''
    if not is_valid_host(host):
        current_app.logger.debug("Error validating host.")
        return Ping(host=host, isdown=True)
    if is_spam(host):
        return Ping(host=host, isdown=True)
    http_host = prefix + host
    is_down = True
    response_code = -1
    current_app.logger.debug("Sending head request to:" + http_host)
    headers = {
        'User-Agent': 'isitdown.site(Check if a site is down)',
    }
    try:
        resp = requests.head(http_host, timeout=2, stream=True, allow_redirects=True, headers=headers)
        # If we come here, we had a response. So the site is up:
        is_down = False
        response_code = resp.status_code
    except Exception as e:
        if "Name or service not known" in repr(e): # TODO: Probably a more informative message would be better.
            return Ping(host=host, isdown=True)

        current_app.logger.error("Exception while contacting {}. Exception: {} ".format(host, e))

        # Check both https and http:
        if "Connection refused" in repr(e) and prefix == "https://":
            return do_ping(host, prefix="http://", from_api=from_api)

    # ip_addr = socket.gethostbyname(host) uh-uh

    p = Ping(from_ip=request.access_route[-1], host=Markup(host),timestamp=datetime.utcnow(), isdown=is_down,
             response_code=response_code, from_api=from_api)

    PingRepository.add_ping(p)

    return p
