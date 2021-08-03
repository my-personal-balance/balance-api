import os
from unittest.mock import MagicMock, patch

import pytest

with patch.dict(
    os.environ,
    {
        "SQLALCHEMY_DATABASE_URI": "postgresql://balance:passw0rd@127.0.0.1:5432/balance_test",
    },
):
    from balance_api.app import app
    from balance_api.api import security
    from balance_api.models.users import User
    from balance_api.connection.db import session_scope, engine
    from balance_api.models import (
        Base
    )
    from balance_api import config


@pytest.fixture(autouse=True)
def patched_environment(monkeypatch):
    monkeypatch.setenv("SQLALCHEMY_DATABASE_URI", "postgresql://balance:passw0rd@127.0.0.1:5432/balance_test",)


@pytest.fixture()
def client():
    app.app.testing = True
    return app.app.test_client()


@pytest.fixture()
def oauth2_token():
    user_data = {
        "id": 1,
        "name": "Test User",
        "email": "test-user@test.com",
    }
    user = User(**user_data)
    return security.generate_token(user)
