import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import JSON


SRC_PATH = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_PATH))

os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from extensions import db
from models import User


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test")
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("CAMPUS_TZ", "UTC")

    from models import Listing

    Listing.__table__.c.dietary_tags.type = JSON()
    from app import create_app

    application = create_app()
    application.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _make_user(role, email):
    user = User(name=role, email=email, role=role)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def vendor(app):
    return _make_user("Vendor", "vendor@example.com")


@pytest.fixture
def student(app):
    return _make_user("Student", "student@example.com")


def login(client, user):
    return client.post(
        "/auth/login",
        data={"email": user.email, "password": "password123"},
    )
