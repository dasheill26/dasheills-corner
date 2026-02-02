import os
import sys
from pathlib import Path
import pytest

# ✅ Ensure project root is importable so "import main" works
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from main import create_app  # noqa: E402
from models import db  # noqa: E402


@pytest.fixture()
def app(monkeypatch):
    # ✅ Use in-memory DB for tests
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["SECRET_KEY"] = "test-secret-key"

    # ✅ Prevent Firestore calls during tests (no metadata server / credentials)
    import main as main_mod
    monkeypatch.setattr(main_mod, "get_menu_items", lambda *args, **kwargs: [])

    a = create_app()
    a.config.update(TESTING=True)

    with a.app_context():
        db.drop_all()
        db.create_all()

    yield a


@pytest.fixture()
def client(app):
    return app.test_client()
