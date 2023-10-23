import os
from datetime import datetime
from unittest.mock import patch

import pytest

with patch.dict(
    os.environ,
    {
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
    },
):
    from balance_api.app import app
    from balance_api.api import security
    from balance_api.connection.db import session_scope, engine
    from balance_api.models import Base
    from balance_api.models.accounts import Account
    from balance_api.models.transactions import Transaction
    from balance_api.models.users import User


@pytest.fixture(autouse=True)
def patched_environment(monkeypatch):
    monkeypatch.setenv(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite://",
    )


@pytest.fixture()
def client(test_db):
    app.app.testing = True
    return app.app.test_client()


@pytest.fixture()
def test_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    scope = session_scope()
    create_models(scope)
    yield scope
    Base.metadata.drop_all(engine)


@pytest.fixture()
def oauth2_token():
    user_data = {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@email.com",
    }
    user = User(**user_data)
    return security.generate_token(user)


def create_models(scope):
    user_mock = {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "currency": "EUR",
    }

    account_mock = {
        "alias": "Account A",
        "type": "CHECKING",
        "currency": "EUR",
    }

    transaction_mock = {
        "date": datetime.now(),
        "transaction_type": "EXPENSE",
        "amount": 100,
        "account_id": 1,
        "description": "Transaction 1",
        "tag_id": None,
    }

    with scope as session:
        session.add(User(**user_mock))
        session.commit()

        user = session.query(User).one()
        if user:
            account = Account(**account_mock)
            account.user_id = user.id
            session.add(account)
            session.commit()

        account = session.query(Account).one()
        if account:
            transaction = Transaction(**transaction_mock)
            transaction.account = account
            session.add(transaction)
            session.commit()
