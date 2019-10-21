from isitdown.repository import Ping, PingRepository
import re
import os
import datetime
from datetime import datetime
import requests
from flask import Markup


class TooManyRequestsException(Exception):
    pass


spam_list = [line.rstrip('\n') for line in open(os.path.dirname(os.path.abspath(__file__)) + '/res/spam.csv')]


def is_spam(host, spam=spam_list):
    return len(list(filter(lambda x: x in host, spam))) > 0


class IsItDown:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def get_last_pings(self):
        return PingRepository.get_last_pings(request_source=0)

    def check(self, host, ip):
        ping = PingRepository.was_down_one_minute_ago(host)
        if ping.isdown:
            ping = self.do_ping(host, ip)
        return ping

    def do_ping(self, host, ip, prefix="https://", from_api=0):
        '''
            Args:
                host: host to ping
                ip: author of the request
                prefix: prefix of the host, either http or https
                from_api: 0 for web, 1 for apiv1, 2 for apiv2 etc.
            @:returns a Ping(), with the result of the ping. It may or may not have been saved on the database.
        '''
        if not self.is_valid_host(host) or is_spam(host):
            return Ping(host=host, isdown=True)
        url = prefix + host
        self.logger.debug("Sending head request to:" + url)
        headers = {
            'User-Agent': 'isitdown.site(Check if a site is down)',
        }
        try:
            resp = requests.head(url, timeout=2, stream=True, allow_redirects=True, headers=headers)
            # If we come here, we had a response. So the site is up:
            p = Ping(from_ip=ip, host=host, timestamp=datetime.utcnow(), isdown=False,
                     response_code=resp.status_code, from_api=from_api)
            PingRepository.add_ping(p)
            return p
        except Exception as e:
            if "Name or service not known" in repr(e):
                return Ping(host=host, isdown=True)

            self.logger.error("Exception while contacting {}. Exception: {} ".format(host, e))

            # Check both https and http:
            if "Connection refused" in repr(e) and prefix == "https://":
                return self.do_ping(host, ip, prefix="http://", from_api=from_api)
            p = Ping(from_ip=ip, host=host, timestamp=datetime.utcnow(), isdown=True,
                     response_code=-1, from_api=from_api)
            PingRepository.add_ping(p)
            return p

    def apiV3(self, host, ip):
        # 1. We return all the pings to this host in the last 30 seconds.
        # 2. if there is a from_ip in the list, return an error.
        pings = PingRepository.last_ping_to(host, self.config['BACKOFF_API_CALL_TIME'])
        for p in pings:
            if p.from_ip == ip:
                raise TooManyRequestsException()

        # there is a recent ping. Let's use that instead of sending a request.
        if len(pings) > 0:
            return pings[-1]

        # If there isn't any ping in the last 30 seconds:
        return self.do_ping(host, ip, from_api=3)

    def is_valid_host(self, host):
        regex = r"((http:\/\/)|(https:\/\/)){0,1}([a-zA-Z0-9-]+\.)+([a-zA-Z])+"
        res = re.compile(regex).match(host)
        if not res:
            self.logger.error("Regex for site: {} not passed.".format(host))
        return res
