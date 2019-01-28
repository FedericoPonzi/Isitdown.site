import os

import pytest
from flask import current_app, g
import isitdown.index as flaskr


def get_db():
    if 'db' not in g:
        g.db = flaskr.db.init_app(current_app)
    return g.db


@pytest.fixture
def client():
    app = flaskr.create_app()
    client = app.test_client()
    yield client


def test_json_api(client):
    resp = client.get('/api/v2/google.it')
    json_data = resp.get_json()
    assert json_data is not None
    assert json_data['isitdown'] is False


def test_working_index(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert rv.status_code == 200
