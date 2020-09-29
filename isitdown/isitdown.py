from isitdown.repository import Ping, PingRepository
import re
import os
import time
import random
from os import path
import datetime
from datetime import datetime
import requests
import socket
from urllib.parse import urlparse
from typing import Optional, List


spam_file_path: str = os.path.dirname(os.path.abspath(__file__)) + '/res/spam.csv'


def load_spam_file() -> List[str]:
    if path.exists(spam_file_path):
        with open(spam_file_path, "r") as f:
            return f.read().splitlines()
    return []


spam_list = load_spam_file()


def is_spam(host: str, spam: Optional[str] =None) -> bool:
    """
    Check if the host is in the spam list.
    :param host:
    :param spam:
    :return:
    """
    if spam is None:
        spam = spam_list
    return len(list(filter(lambda x: x in host, spam))) > 0


def get_last_pings():
    return PingRepository.get_last_pings(request_source=0)


def get_host_from_url(host: str) -> str:
    return urlparse(host).netloc or host


class IsItDown:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def do_ping(self, host: str, ip: str, from_api: int, prefix: str = "https://") -> Ping:
        """
            Args:
                host: host to ping
                ip: author of the request
                prefix: prefix of the host, either http or https
                from_api: 0 for web, 1 for apiv1, 2 for apiv2 etc.
            @:returns a Ping(), with the result of the ping. It may or may not have been saved on the database.
        """
        if not self.is_valid_host(host) or is_spam(host):
            return Ping(host=host, isdown=True)
        url = prefix + host
        self.logger.debug("Sending head request to:" + url)
        headers = {
            'User-Agent': 'isitdown.site(Check if a site is down)',
        }
        resp_code = Ping.RESPONSE_DOWN
        try:
            resp = requests.head(url, timeout=2, stream=True, allow_redirects=True, headers=headers)
            # If we come here, we had a response. So the site is up:
            resp_code = resp.status_code
        finally:
            p = Ping(from_ip=ip, host=host, timestamp=datetime.utcnow(), isdown=resp_code == Ping.RESPONSE_DOWN,
                     response_code=resp_code, from_api=from_api)
            PingRepository.add_ping(p)
            return p

    def check_api_v3(self, url, ip, from_api):
        host = get_host_from_url(url)
        pings_from_host = PingRepository.requests_quantity_from(ip, 60)
        if pings_from_host > 10:
            time.sleep(1 + random.randint(1, 5))
            return Ping.get_invalid_ping(host)

        if not self.is_valid_host(host) or is_spam(host) or not self.hostname_exists(host):
            return Ping.get_invalid_ping(host)
        # 1. We return all the pings to this host in the last 30 seconds.
        pings = PingRepository.last_ping_to(host, self.config['BACKOFF_API_CALL_TIME'])

        # there is a recent ping. Let's use that instead of sending a request.
        if len(pings) > 0:
            return pings[-1]

        # If there isn't any ping in the last 30 seconds:
        return self.do_ping(host, ip, from_api)

    @staticmethod
    def hostname_exists(host: str) -> bool:
        try:
            socket.gethostbyname(host)
        except socket.gaierror:
            return False
        else:
            return True

    @staticmethod
    def is_valid_host(host) -> bool:
        host = host.lower()
        # TODO: this regex is probably too restrictive wrt utf8.
        regex = r"^(http:\/\/|https:\/\/){0,1}[a-z0-9\.\-]+?\.[a-z]+\.?\/?$"
        return re.compile(regex).match(host) is not None