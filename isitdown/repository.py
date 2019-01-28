from datetime import datetime, timedelta
from sqlalchemy import desc
from sqlalchemy.sql.expression import and_
from .index import db
from .models import Ping


class PingRepository:
    """ Repository class for the Ping table. Used to do queries against the database."""

    @staticmethod
    def getLastPings(n=10):
        '''
        :param n:
        :return: the last n pings
        '''
        p = db.session.query(Ping.host, Ping.isdown, Ping.response_code, db.func.max(Ping.timestamp).label("timestamp"))\
            .order_by(desc("timestamp")).group_by(Ping.host, Ping.isdown, Ping.response_code).limit(n)
        return p.all()


    @staticmethod
    def wasDownOneMinuteAgo(host):
        """
            Caches/limit requests to down sites to 1 per minute.
            Returns
            ------
            True, if the host was reported as up in the last minute
            False, otherwise.
        """
        oneMinuteAgo = datetime.utcnow() - timedelta(minutes=1)
        last = Ping.query.filter(and_(Ping.host == host, oneMinuteAgo < Ping.timestamp)).all()
        if len(last) > 0:
            return last[0]
        return Ping(host=host, isdown=True, response_code="-1") # We have no informations, so assume was down.

    @staticmethod
    def addPing(p):
        db.session.add(p)
        db.session.commit()

