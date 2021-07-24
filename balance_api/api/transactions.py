from flask import jsonify
from sqlalchemy.orm.session import Session

from balance_api.api import Resource
from balance_api.api.account_tags import AccountTagResource
from balance_api.api.accounts import AccountResource
from balance_api.connection.db import database_operation
from balance_api.exceptions import ResourceBadRequest
from balance_api.models.transaction_asset import (
    create_transaction_asset_with_isin
)
from balance_api.models.transactions import (
    Transaction,
    TransactionType,
    create_transaction as create_t,
    delete_transaction as delete_t,
    list_transactions as list_t,
    get_balance,
)
from balance_api.transactions.loader import TransactionFileLoader


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

        return transaction_resource


@database_operation(max_tries=3)
def list_transactions(
        account_id: int = None,
        period_type: int = None,
        period_offset: int = None,
        start_date: int = None,
        end_date: int = None,
        session: Session = None,
        **kwargs,
):
    user_id = dict(kwargs)["user"]
    transactions = list_t(
        int(user_id),
        account_id,
        period_type,
        period_offset,
        start_date,
        end_date,
        session
    )

    balance, incomes, expenses = get_balance(
        int(user_id),
        account_id,
        period_type,
        period_offset,
        start_date,
        end_date,
        session
    )

    response = jsonify({
        "transactions": [TransactionResource(transaction).serialize() for transaction in transactions],
        "balance": balance,
        "incomes": incomes,
        "expenses": expenses
    })

    session.close()

    return response


@database_operation(max_tries=3)
def create_transaction(session: Session, **transaction):
    transaction_data = transaction["body"]
    transaction_resource = TransactionResource.deserialize(transaction_data, create=True)
    new_transaction = create_t(transaction_resource, session)

    if new_transaction.transaction_type == TransactionType.INVESTMENT:
        if "asset" in transaction_data:
            isin = transaction_data.get("asset").get("isin", None)
            create_transaction_asset_with_isin(
                new_transaction,
                isin=isin,
                session=session
            )
        else:
            raise ResourceBadRequest(detail="No asset info given for an Investment transaction.")

    return jsonify(TransactionResource(new_transaction).serialize()), 201


@database_operation(max_tries=3)
def delete_transaction(transaction_id: int, session: Session, **kwargs):
    user_id = dict(kwargs)["user"]
    delete_t(user_id, transaction_id, session)
    return 204


@database_operation(max_tries=3)
def upload_transaction(session: Session, **kwargs):
    transaction = dict(kwargs)
    user_id = transaction["user"]

    account_id = None
    if "body" in kwargs:
        account_id = transaction["body"].get("account_id")

    if "file" not in transaction:
        raise ResourceBadRequest(detail="Transaction file data not received")

    if account_id:
        file = transaction["file"]
        transaction_file_loader = TransactionFileLoader(
            file=file,
            user_id=user_id,
            account_id=account_id,
            session=session,
        )

        try:
            transaction_file_loader.process()
        except Exception:
            raise ResourceBadRequest(detail="Error while loading the transaction file")

        return jsonify({"success": True}), 201
    else:
        raise ResourceBadRequest(detail="No account id information found in the request")


