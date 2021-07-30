import uuid

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
                "type": account.type.name if account.type else None,
            }
        )

        resource.update(**kwargs)

        return resource

    @classmethod
    def deserialize(cls, account_data: dict, create=True) -> dict:
        account_resource = {}

        for field in cls.fields:
            account_resource[field] = account_data.get(field, None)
        for field in cls.protected_fields:
            account_resource.pop(field, None)

        return account_resource


@database_operation(max_tries=3)
def find_account(account_id: uuid, session: Session, **kwargs):
    user_id = dict(kwargs)["user"]
    account = find_a(user_id, account_id, session)
    if not account:
        return {}, 404

    account_resource = get_account_financial_data(account, session)
    return jsonify(account_resource)


@database_operation(max_tries=3)
def list_accounts(session: Session, **kwargs):
    user_id = dict(kwargs)["user"]
    accounts = []
    for account in list_a(user_id, session):
        account_resource = get_account_financial_data(account, session)
        accounts.append(account_resource)

    return jsonify({"accounts": accounts})


def get_account_financial_data(account: Account, session: Session) -> dict:
    balance, incomes, expenses = get_balance(
        user_id=account.user_id, account_id=account.id, session=session
    )

    account = AccountResource(account).serialize(
        **{
            "balance": balance,
            "incomes": incomes,
            "expenses": expenses,
        }
    )

    return account


@database_operation(max_tries=3)
def create_account(session: Session, **kwargs):
    user_id = dict(kwargs)["user"]
    account_resource = AccountResource.deserialize(kwargs["body"], create=True)
    account_resource["user_id"] = user_id
    new_account = create_a(account_resource, session)
    return jsonify(AccountResource(new_account).serialize()), 201
