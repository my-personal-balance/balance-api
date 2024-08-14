import pytest

from balance_api.api import security
from balance_api.app import app
from balance_api.data.models import User


@pytest.fixture(autouse=True)
def patched_environment(monkeypatch):
    monkeypatch.setenv(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql+psycopg://balance:passw0rd@127.0.0.1:5432/balance_test",
    )
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")


@pytest.fixture()
def client():
    app.testing = True
    return app.test_client()


@pytest.fixture()
def oauth2_token():
    user_data = {
        "id": 1,
        "name": "Test User",
        "email": "test-user@test.com",
    }
    user = User(**user_data)
    return security.generate_token(user)
