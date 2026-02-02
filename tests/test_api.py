import os
import pytest
from main import create_app
from models import db

@pytest.fixture()
def app():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["SECRET_KEY"] = "test"
    a = create_app()
    a.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with a.app_context():
        db.create_all()
    yield a

@pytest.fixture()
def client(app):
    return app.test_client()

def test_menu_api(client):
    r = client.get("/api/menu")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)
