import time
import pytest
from flask import current_app, g
import isitdown.index as flaskr
from isitdown.config import TestingConfig
from datetime import datetime


def get_db():
    if 'db' not in g:
        g.db = flaskr.db
    return g.db


@pytest.fixture
def client():
    app = flaskr.create_app()
    with app.app_context():
        flaskr.db.create_all()
    app.config.from_object(TestingConfig)
    client = app.test_client()
    yield client, app


def test_working_index(client):
    client, app = client
    """Start with a blank database."""
    rv = client.get('/')
    assert rv.status_code == 200


def test_apiv2(client):
    client, app = client
    resp = client.get('/api/v2/google.it')
    json_data = resp.get_json()
    print(app.config['BACKOFF_API_CALL_TIME'])
    assert json_data is not None
    assert json_data['isitdown'] is False


def test_apiv3(client):

    client, app = client
    resp = client.get('/api/v3/google.it')
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data is not None
    assert json_data['isitdown'] is False
    assert json_data['host'] == "google.it"


def test_backoff(client):
    client, app = client
    backoff_time = 2
    resp = client.get("/api/v3/google.it")
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data is not None
    assert json_data['isitdown'] is False
    start_time = datetime.now()
    app.config.BACKOFF_API_CALL_TIME = backoff_time
    while (start_time - datetime.now()).seconds <= (backoff_time) - 1:
        resp = client.get("/api/v3/google.it")
        assert(resp.status_code == 429)
    time.sleep(1)
    resp = client.get("/api/v3/google.it")
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data is not None
    assert json_data['isitdown'] is False

def millis(start_time):
    """
    :param start_time: datetime.datetime 
    :return: milliseconds elapsed from that datetime.
    """
    dt = datetime.now() - start_time
    ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
    return ms


