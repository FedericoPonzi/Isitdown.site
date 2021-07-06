from datetime import datetime, timedelta
from sqlalchemy import desc
from sqlalchemy.sql.expression import and_
from .index import db
from .models import Ping


class PingRepository:
    """ Repository class for the Ping table. Used to do queries against the database."""

    @staticmethod
    def get_last_pings(n=10, request_source=0):
        """
        :param n: number of last pings to get
        :param request_source: select the source of the last pings. -1 for every request source
        :return: the last n pings
        """
        p = db.session.query(Ping.host, Ping.isdown, Ping.response_code,
                             db.func.max(Ping.timestamp).label("timestamp")) \
            .order_by(desc("timestamp"))
        if request_source >= 0:
            p = p.filter(Ping.from_api == request_source)
        p = p.group_by(Ping.host, Ping.isdown, Ping.response_code).limit(n)
        return p.all()

    @staticmethod
    def requests_quantity_from(ip, seconds):
        delta = datetime.utcnow() - timedelta(seconds=seconds)
        return Ping.query.filter(and_(Ping.from_ip == ip, delta < Ping.timestamp)).count()

    @staticmethod
    def last_ping_to(host, millis):
        """
        :param host: hostname, string
        :param millis: milliseconds, int
        :return: a list of pings in the last `millis` to host.
        """
        delta = datetime.utcnow() - timedelta(milliseconds=millis)
        return Ping.query.filter(and_(Ping.host == host, delta < Ping.timestamp)).all()

    @staticmethod
    def add_ping(p):
        db.session.add(p)
        db.session.commit()
