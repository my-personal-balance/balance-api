from flask import jsonify
from sqlalchemy.orm.session import Session

from balance_api.api import Resource
from balance_api.connection.db import database_operation
from balance_api.models.accounts import (
    Account,
    find_account as find_a,
    list_accounts as list_a,
    create_account as create_a,
)
from balance_api.models.transactions import get_balance


class AccountResource(Resource):
    fields = [
        "id",
        "alias",
        "user_id",
        "type",
    ]

    protected_fields = [
        "created_at",
        "updated_at",
    ]

    def serialize(self, **kwargs) -> dict:
        resource = super().serialize()
        account: Account = self.instance

        resource.update(
            {
                "id": account.id,
                "alias": account.alias,
                "user_id": account.user_id,
                "type": account.type.name,
            }
        )

        resource.update(**kwargs)

        return resource

    @classmethod
    def deserialize(cls, user_id: int, account_data: dict, create=True) -> dict:
        account_resource = {}

        for field in cls.fields:
            account_resource[field] = account_data.get(field, None)
        for field in cls.protected_fields:
            account_resource.pop(field, None)

        account_resource["user_id"] = user_id

        return account_resource


@database_operation(max_tries=3)
def find_account(user_id: int, account_id: int, session: Session):
    account = find_a(user_id, account_id, session)
    if not account:
        return {}, 404

    account_balance = get_balance(user_id, account_id, session)

    response = jsonify(AccountResource(account).serialize(**{
        "balance": account_balance
    }))
    return response


@database_operation(max_tries=3)
def list_accounts(user_id: int, session: Session):
    accounts = []
    for account in list_a(user_id, session):
        account_balance = get_balance(user_id, account.id, session)
        account = AccountResource(account).serialize(**{
            "balance": account_balance
        })
        accounts.append(account)

    return jsonify({"accounts": accounts})


@database_operation(max_tries=3)
def create_account(user_id: int, session: Session, **account):
    account_resource = AccountResource.deserialize(user_id, account["body"], create=True)
    new_account = create_a(account_resource, session)
    return jsonify(AccountResource(new_account).serialize()), 201
