def test_accounts_find_account(client, oauth2_token):
    response = client.get(f"/accounts/{1}", headers={"Authorization": f"Bearer {oauth2_token}"})
    assert response.status_code == 200
    account = response.json
    assert account["id"] == 1


def test_accounts_list_accounts(client, oauth2_token):
    response = client.get("/accounts", headers={"Authorization": f"Bearer {oauth2_token}"})
    assert response.status_code == 200
    assert len(response.json["accounts"]) == 1


def test_accounts_get_account_financial_data(client, oauth2_token):
    pass


def test_accounts_create_account(client, oauth2_token):
    pass


def test_accounts_delete_account(client, oauth2_token):
    pass


def test_accounts_get_account_balance(client, oauth2_token):
    pass