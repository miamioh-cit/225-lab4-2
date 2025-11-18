import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as c:
        yield c

def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.get_json().get('status') == 'ok'
