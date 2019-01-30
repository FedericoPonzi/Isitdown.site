import os

import pytest
from flask import current_app, g
import isitdown.index as flaskr


def get_db():
    if 'db' not in g:
        g.db = flaskr.db
    return g.db


@pytest.fixture
def client():
    app = flaskr.create_app()
    with app.app_context():
        flaskr.db.create_all()
    client = app.test_client()
    yield client


def test_working_index(client):
    """Start with a blank database."""
    rv = client.get('/')
    assert rv.status_code == 200


def test_apiv2(client):
    resp = client.get('/api/v2/google.it')
    json_data = resp.get_json()
    assert json_data is not None
    assert json_data['isitdown'] is False


def test_apiv3(client):
    resp = client.get('/api/v3/google.it')
    json_data = resp.get_json()
    assert json_data is not None
    assert json_data['isitdown'] is False
    assert json_data['host'] == "google.it"

