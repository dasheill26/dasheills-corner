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

def test_register_and_login(client):
    r = client.post("/register", data={"name":"Test User", "email":"t@example.com", "password":"password123"}, follow_redirects=True)
    assert r.status_code == 200

    client.post("/logout", follow_redirects=True)

    r2 = client.post("/login", data={"email":"t@example.com", "password":"password123"}, follow_redirects=True)
    assert r2.status_code == 200
