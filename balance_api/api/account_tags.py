from flask import jsonify
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

from balance_api.api import Resource
from balance_api.connection.db import database_operation
from balance_api.models.account_tags import AccountTag


class AccountTagResource(Resource):
    fields = [
        "id",
        "value",
        "account_id",
    ]

    protected_fields = [
        "created_at",
        "updated_at",
    ]

    def serialize(self) -> dict:
        resource = super().serialize()
        account_tag: AccountTag = self.instance

        resource.update(
            {
                "id": account_tag.id,
                "value": account_tag.value,
                "account_id": account_tag.account_id,
            }
        )

        return resource

    @classmethod
    def deserialize(cls, account_id: int, account_tag_data: dict, create=True) -> dict:
        account_tag_resource = {}

        for field in cls.fields:
            account_tag_resource[field] = account_tag_data.get(field, None)
        for field in cls.protected_fields:
            account_tag_resource.pop(field, None)

        account_tag_resource["account_id"] = account_id

        return account_tag_resource


@database_operation(max_tries=3)
def find_account_tag(account_id: int, account_tag_id: int, session: Session):
    q = (
        session.query(AccountTag).where(AccountTag.account_id == account_id, AccountTag.id == account_tag_id)
    )
    try:
        account_tag = q.one()
    except NoResultFound:
        return {}, 404

    return jsonify(AccountTagResource(account_tag).serialize())


@database_operation(max_tries=3)
def list_account_tags(user_id: int, account_id: int, session: Session):
    q = (
        session.query(AccountTag).where(AccountTag.account_id == account_id).order_by(AccountTag.id)
    )
    account_tags = [
        AccountTagResource(account_tag).serialize() for account_tag in q.all()
    ]
    return jsonify({"items": account_tags})

