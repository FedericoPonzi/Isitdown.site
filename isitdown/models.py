from .index import db


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


class Ping(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    from_ip = db.Column(db.String(120))
    host = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    isdown = db.Column(db.Boolean)
    response_code = db.Column(db.Integer)
    from_api = db.Column(db.Integer)  # 0 = from frontend, 1 = from apis TODO: rename to request_source

    def __repr__(self):
        return 'Pings(id=%r, from= %r, to= %r, at=%r, isdown=%r, response=%dr)' % (self.id, self.from_ip, self.host,
                                                                                   self.time_stamp, self.isdown,
                                                                                   self.response_code)
