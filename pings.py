import subprocess
import requests
from urllib3.exceptions import ReadTimeoutError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import and_
from sqlalchemy import desc

from datetime import datetime, timedelta

#from sqlalchemy.dialects import postgresql
db = SQLAlchemy()

class Pings(db.Model):
    __tablename__ = "pings"
    id = db.Column(db.Integer, primary_key=True)
    f = db.Column(db.String(120)) # from
    t = db.Column(db.String(120)) # to
    at = db.Column(db.DateTime) # at
    down = db.Column(db.Boolean) # is it down?

    def __init__(self, f, t, at, d):
        self.f = f
        self.t = t
        self.at = at
        self.down = d

    def __repr__(self):
        return 'Pings(id=%r, from= %r, to= %r, at=%r, down=%r)' % (self.id, self.f, self.t, self.at, self.down)

class PingsRepository():
    """ Repository class for the Pings table. Used to do queries against the database."""
    @staticmethod
    def getLastPings(n=10):
        p = db.session.query(Pings.t, Pings.down, db.func.max(Pings.at).label("at")).order_by(desc("at")).group_by(Pings.t, Pings.down).limit(10)
        return p.all()

    @staticmethod
    def isLastPingSuccessfull(host):
        """
            Caches/limit requests to down sites to 1 per minute.
            Returns
            ------
            True, if the host was reported as up in the last minute
            False, otherwise.
        """
        oneMinuteAgo = datetime.utcnow() - timedelta(minutes=1)
        last = Pings.query.filter(and_(Pings.t == host, oneMinuteAgo < Pings.at )).all()
        return len(last) > 0 and last[0].down

    @staticmethod
    def addPing(p):
        db.session.add(p)
        db.session.commit()

