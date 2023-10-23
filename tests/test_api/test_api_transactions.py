
def test_transactions_list_transactions(client, oauth2_token):
    response = client.get("/transactions", headers={"Authorization": f"Bearer {oauth2_token}"})
    assert response.status_code == 200
    assert len(response.json["transactions"]) == 1


def test_transactions_create_transaction(client, oauth2_token):
    pass


def test_transactions_update_transaction(client, oauth2_token):
    pass


def test_transactions_batch_updates_transactions(client, oauth2_token):
    pass


def test_transactions_upload_transaction(client, oauth2_token):
    pass
