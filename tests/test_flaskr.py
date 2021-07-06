import time
import pytest
from flask import g
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
    # Start with a blank database.
    rv = client.get('/')
    assert rv.status_code == 200


def test_route_not_exists(client):
    client, app = client
    rv = client.get("/something/something")
    assert rv.status_code == 404


def test_robots(client):
    client, app = client
    rv = client.get("/robots.txt")
    assert rv.status_code == 200


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

def test_is_valid_host():
    from isitdown.isitdown import IsItDown
    assert IsItDown.is_valid_host("https://google.it")
    assert IsItDown.is_valid_host("https://google.com")
    assert IsItDown.is_valid_host("https://www.google.com")
    assert IsItDown.is_valid_host("https://hey.google.com")
    assert IsItDown.is_valid_host("https://hey.google.com/")
    assert IsItDown.is_valid_host("https://hey.google.com.")
    assert not IsItDown.is_valid_host("https://hey.google.com/something")
    assert not IsItDown.is_valid_host("https://hey.google.com./something")
    assert not IsItDown.is_valid_host("https:/.google.com")
    assert not IsItDown.is_valid_host("htts://.google.com")
    assert not IsItDown.is_valid_host("htts://.google.com")
    assert not IsItDown.is_valid_host("htts://com.google.com")
    assert not IsItDown.is_valid_host("https://com.google.co3333m")