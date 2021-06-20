from flask import jsonify
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

from balance_api.api import Resource
from balance_api.connection.db import database_operation
from balance_api.models.transactions import Transaction
from balance_api.api.account_tags import AccountTagResource


class TransactionResource(Resource):
    fields = [
        "id",
        "previous_transaction_id",
        "date",
        "transaction_type",
        "amount",
        "account_id",
        "description",
        "account_tag_id",
    ]

    protected_fields = [
        "created_at",
        "updated_at",
    ]

    def serialize(self) -> dict:
        resource = super().serialize()
        transaction: Transaction = self.instance

        resource.update(
            {
                "id": transaction.id,
                "previous_transaction_id": transaction.previous_transaction_id,
                "date": transaction.date,
                "transaction_type": transaction.transaction_type.name,
                "amount": transaction.amount,
                "account_id": transaction.account_id,
                "description": transaction.description,
                "tag": AccountTagResource(transaction.account_tag).serialize(),
            }
        )

        return resource

    @classmethod
    def deserialize(cls, account_id: int, transaction_data: dict, create=True) -> dict:
        transaction_resource = {}

        for field in cls.fields:
            transaction_resource[field] = transaction_data.get(field, None)
        for field in cls.protected_fields:
            transaction_resource.pop(field, None)

        transaction_resource["account_id"] = account_id

        return transaction_resource


@database_operation(max_tries=3)
def find_transaction(user_id: int, account_id: int, transaction_id: int, session: Session):
    q = (
        session.query(Transaction).where(Transaction.account_id == account_id, Transaction.id == transaction_id)
    )
    try:
        transaction = q.one()
    except NoResultFound:
        return {}, 404

    return jsonify(TransactionResource(transaction).serialize())


@database_operation(max_tries=3)
def list_transactions(user_id: int, account_id: int, session: Session):
    q = (
        session.query(Transaction).where(Transaction.account_id == account_id).order_by(Transaction.date)
    )
    transactions = [
        TransactionResource(transaction).serialize() for transaction in q.all()
    ]
    return jsonify({"items": transactions})

