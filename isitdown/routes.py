from flask import render_template, request, jsonify, send_from_directory, Blueprint, current_app

import os
from .isitdown import IsItDown, get_last_pings
from werkzeug.local import LocalProxy

basedir = os.path.abspath(os.path.dirname(__file__))

frontend_bp = Blueprint('index', __name__, static_folder=os.path.join(basedir, "static"), template_folder="templates")
config = LocalProxy(lambda: current_app.config)
logger = LocalProxy(lambda: current_app.logger)

isitdown = IsItDown(config=config, logger=logger)


@frontend_bp.route("/api/v3/<string:url>")
def api_v3(url=""):
    """
    api v3 impl
    :param url: In theory, we expect an host, but client's are always clever.
    :return: a json response object.
    """
    ip = request.access_route[-1]
    res = isitdown.check_api_v3(url, ip, 3)
    return jsonify(isitdown=res.isdown, response_code=res.response_code, host=res.host, deprecated=False)


# Some static files:
@frontend_bp.route("/favicon.ico")
@frontend_bp.route("/robots.txt")
@frontend_bp.route("/sitemap.xml")
@frontend_bp.route("/humans.txt")
def get_robots():
    return send_from_directory(frontend_bp.static_folder, request.path[1:])


@frontend_bp.route("/")
@frontend_bp.route("/<string:host>")
def check(host=""):
    ip = request.access_route[-1]
    last_ping_list = get_last_pings()
    if len(host) == 0:
        return render_template("index.html", last=last_ping_list)
    ping = isitdown.check_api_v3(host, ip, 0)
    return render_template("check.html", last=last_ping_list, pingres=ping)


@frontend_bp.errorhandler(404)
def page_not_found(error):
    current_app.logger.error(error)
    return render_template('404.html'), 404
