from datetime import datetime, timedelta

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from sqlalchemy.sql.expression import and_

# from sqlalchemy.dialects import postgresql
db = SQLAlchemy()


class Pings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_ip = db.Column(db.String(120))
    host = db.Column(db.String(120))
    time_stamp = db.Column(db.DateTime)
    isdown = db.Column(db.Boolean)
    response_code = db.Column(db.Integer)

    '''   def __init__(self, from_ip, host, time_stamp, isdown, response_code):
        def __init__(**kwargs):
            super(Foo, self).__init__(**kwargs)
        self.response_code = response_code
        self.isdown = isdown
        self.time_stamp = time_stamp #at
        self.host = host #t
        self.from_ip = from_ip
    '''
    def __repr__(self):
        return 'Pings(id=%r, from= %r, to= %r, at=%r, isdown=%r, response=%dr)' % (self.id, self.from_ip, self.host, self.time_stamp, self.isdown, self.response_code)

class PingsRepository:
    """ Repository class for the Pings table. Used to do queries against the database."""

    @staticmethod
    def getLastPings(n=10):
        '''
        :param n:
        :return: the last n pings
        '''
        p = db.session.query(Pings.host, Pings.isdown, Pings.response_code, db.func.max(Pings.time_stamp).label("time_stamp"))\
            .order_by(desc("time_stamp")).group_by(Pings.host, Pings.isdown, Pings.response_code).limit(n)
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
        last = Pings.query.filter(and_(Pings.host == host, oneMinuteAgo < Pings.time_stamp)).all()
        return len(last) > 0 and last[0].isdown

    @staticmethod
    def addPing(p):
        db.session.add(p)
        db.session.commit()

