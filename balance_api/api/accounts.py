from flask import jsonify
from sqlalchemy.orm.session import Session

from balance_api.api import Resource
from balance_api.connection.db import database_operation
from balance_api.models.accounts import Account
from sqlalchemy.exc import NoResultFound

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

    def serialize(self) -> dict:
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
    q = (
        session.query(Account).where(Account.user_id == user_id, Account.id == account_id)
    )
    try:
        account = q.one()
    except NoResultFound:
        return {}, 404

    return jsonify(AccountResource(account).serialize())


@database_operation(max_tries=3)
def list_accounts(user_id: int, session: Session):
    q = (
        session.query(Account).where(Account.user_id == user_id).order_by(Account.id)
    )
    accounts = [
        AccountResource(account).serialize() for account in q.all()
    ]
    return jsonify({"items": accounts})


@database_operation(max_tries=3)
def create_account(user_id: int, session: Session, **account):
    account_resource = AccountResource.deserialize(user_id, account["body"], create=True)
    new_account = Account(**account_resource)
    session.add(new_account)
    session.commit()

    return jsonify(AccountResource(new_account).serialize()), 201
