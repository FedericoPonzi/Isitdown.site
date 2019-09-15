import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = os.environ.get("ISITDOWN_DATABASE_URI", 'sqlite:///' + os.path.join(basedir, 'app.db'))
    SECRET_KEY = os.environ.get('ISITDOWN_SECRET_KEY', 'you-will-never-guess')
    SQLALCHEMY_DATABASE_URI = str(DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    BACKOFF_API_CALL_TIME = 30 * 1e3 # ms


class DevelopmentConfig(Config):
    DEBUG = True
    BACKOFF_API_CALL_TIME = 2 * 1e3 # ms


class TestingConfig(Config):
    TESTING = True
    BACKOFF_API_CALL_TIME = 0  # ms
