import tempfile
import uuid

from flask import jsonify
from sqlalchemy.orm.session import Session

from balance_api.api import Resource
from balance_api.api.account_tags import AccountTagResource
from balance_api.api.accounts import AccountResource
from balance_api.connection.db import database_operation
from balance_api.models.transactions import (
    Transaction,
    delete_transaction as delete_t,
    list_transactions as list_t,
    get_balance,
)
from balance_api.transactions.loader import process_transactions_file, SourceFileType
from balance_api.transactions.mappings import n26


class TransactionResource(Resource):
    fields = [
        "id",
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
                "date": transaction.date,
                "transaction_type": transaction.transaction_type.name,
                "amount": transaction.amount,
                "account": AccountResource(transaction.account).serialize(),
                "description": transaction.description,
                "tag": AccountTagResource(transaction.account_tag).serialize() if transaction.account_tag else None,
            }
        )

        return resource

    @classmethod
    def deserialize(cls, transaction_data: dict, create=True) -> dict:
        transaction_resource = {}

        for field in cls.fields:
            transaction_resource[field] = transaction_data.get(field, None)
        for field in cls.protected_fields:
            transaction_resource.pop(field, None)

        account = transaction_data.get("account", None)
        transaction_resource["account_id"] = account.get("id", None) if account else None

        return transaction_resource


@database_operation(max_tries=3)
def list_transactions(
        user_id: int,
        account_id: uuid = None,
        period_type: int = None,
        period_offset: int = None,
        start_date: int = None,
        end_date: int = None,
        session: Session = None):

    transactions = list_t(
        user_id,
        account_id,
        period_type,
        period_offset,
        start_date,
        end_date,
        session
    )

    balance, incomes, expenses = get_balance(
        user_id,
        account_id,
        period_type,
        period_offset,
        start_date,
        end_date,
        session
    )

    return jsonify({
        "transactions": [TransactionResource(transaction).serialize() for transaction in transactions],
        "balance": balance,
        "incomes": incomes,
        "expenses": expenses
    })


@database_operation(max_tries=3)
def create_transaction(user_id: int, session: Session, **transaction):
    transaction_resource = TransactionResource.deserialize(transaction["body"], create=True)
    new_transaction = Transaction(**transaction_resource)
    new_transaction.amount = abs(new_transaction.amount)
    session.add(new_transaction)
    session.commit()

    return jsonify(TransactionResource(new_transaction).serialize()), 201


@database_operation(max_tries=3)
def delete_transaction(user_id: int, transaction_id: uuid, session: Session):
    delete_t(user_id, transaction_id, session)
    return 204


@database_operation(max_tries=3)
def upload_transaction(user_id: int, session: Session, **transaction):
    if "body" in transaction:
        account_id = transaction["body"].get("account_id", None)

    if "file" in transaction:
        file = transaction["file"]

    if account_id and file:
        with tempfile.NamedTemporaryFile() as f:
            file.save(f.name)
            process_transactions_file(f, SourceFileType.CSV, n26.mapping, account_id, session)

    return jsonify({"success": True}), 201