import pytest

from balance_api.connection.db import session_scope
from balance_api import config


def test_transactions_list_transactions(client, oauth2_token):

    response = client.get("/transactions", headers={"Authorization": f"Bearer {oauth2_token}"})

    assert response.status_code == 200
    assert len(response.json["transactions"]) == 4
    # assert response.json["transactions"][0] == transaction
