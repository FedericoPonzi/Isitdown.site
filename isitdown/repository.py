from datetime import datetime, timedelta
from sqlalchemy import desc
from sqlalchemy.sql.expression import and_
from .index import db
from .models import Ping


class PingRepository:
    """ Repository class for the Ping table. Used to do queries against the database."""

    @staticmethod
    def get_last_pings(n=10, request_source=0):
        '''
        :param n: number of last pings to get
        :param request_source: select the source of the last pings. -1 for every request source
        :return: the last n pings
        '''
        p = db.session.query(Ping.host, Ping.isdown, Ping.response_code, db.func.max(Ping.timestamp).label("timestamp"))\
            .order_by(desc("timestamp"))
        if request_source >= 0:
            p = p.filter(Ping.from_api == request_source)
        p = p.group_by(Ping.host, Ping.isdown, Ping.response_code).limit(n)
        return p.all()

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
    def was_down_one_minute_ago(host):
        """
            @Returns
            The last ping, if the host was pinged as up in the last minute
                           else A new Ping(isitdown=False) if we don't have informations.
        """
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        last = Ping.query.filter(and_(Ping.host == host, one_minute_ago < Ping.timestamp)).all()
        if len(last) > 0:
            return last[0]
        return Ping(host=host, isdown=True, response_code="-1") # We have no informations, so assume was down.

    @staticmethod
    def add_ping(p):
        db.session.add(p)
        db.session.commit()


