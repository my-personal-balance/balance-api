from flask import jsonify
from sqlalchemy.orm.session import Session

from balance_api.api import Resource
from balance_api.connection.db import database_operation
from balance_api.models.split_transactions import (
    SplitTransaction,
    create_split_transactions,
    list_split_transactions,
)


class SplitTransactionResource(Resource):
    fields = ["id", "transaction_id", "amount", "description", "tag_id"]

    protected_fields = [
        "created_at",
        "updated_at",
    ]

    def serialize(self) -> dict:
        resource = super().serialize()
        split_trans: SplitTransaction = self.instance

        resource.update(
            {
                "id": split_trans.id,
                "transaction_id": split_trans.transaction_id,
                "amount": split_trans.amount,
                "description": split_trans.description,
                "tag_id": split_trans.tag_id,
            }
        )

        return resource

    @classmethod
    def deserialize(cls, split_transaction_data: dict, create=True) -> dict:
        split_transaction_resource = {}

        for field in cls.fields:
            split_transaction_resource[field] = split_transaction_data.get(field, None)
        for field in cls.protected_fields:
            split_transaction_resource.pop(field, None)

        return split_transaction_resource


@database_operation(max_tries=3)
def split_transaction(transaction_id: int, session: Session, **kwargs):
    user_id = dict(kwargs)["user"]

    if "transactions" in kwargs["body"]:
        transactions_data = kwargs["body"]["transactions"]

        split_transactions = [
            SplitTransactionResource.deserialize(transaction_data, create=True)
            for transaction_data in transactions_data
        ]

        create_split_transactions(
            user_id=user_id,
            transaction_id=transaction_id,
            split_transactions=split_transactions,
            session=session,
        )

        split_transactions = list_split_transactions(
            user_id=user_id, transaction_id=transaction_id, session=session
        )

        return (
            jsonify(
                {
                    "split_transactions": [
                        SplitTransactionResource(transaction).serialize()
                        for transaction in split_transactions
                    ],
                }
            ),
            200,
        )
