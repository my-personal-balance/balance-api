import logging

from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm.session import Session

from balance_api.data.db import database_operation
from balance_api.data.dtos.transactions import Transaction
from balance_api.data.models.transactions import (
    PeriodType,
    create_transaction as create_t,
    delete_transaction as delete_t,
    list_transactions as list_t,
    patch_transaction,
    update_transaction as update_t,
)
from balance_api.transactions.loader import TransactionFileLoader

logger = logging.getLogger(__name__)

bp = Blueprint("transactions", __name__)


@bp.get("/transactions")
@jwt_required()
@database_operation(max_tries=3)
def list_transactions(session: Session):
    user_id = get_jwt_identity()
    account_id = request.args.get("account_id", type=int)
    tag_id = request.args.get("tag_id", type=int)
    period_type = request.args.get("period_type", type=PeriodType)
    period_offset = request.args.get("period_offset", type=int)
    start_date = request.args.get("start_date", type=str)
    end_date = request.args.get("end_date", type=str)

    max_results = None if period_type else 100

    transactions = list_t(
        int(user_id),
        account_id,
        tag_id,
        period_type,
        period_offset,
        start_date,
        end_date,
        max_results,
        session,
    )

    response = jsonify({"transactions": Transaction.serialize_many(transactions)})

    session.close()

    return response


@bp.post("/transactions")
@jwt_required()
@database_operation(max_tries=3)
def create_transaction(session: Session):
    user_id = get_jwt_identity()
    transaction_data = request.json
    new_transaction = create_t(int(user_id), transaction_data, session)
    return jsonify(Transaction.serialize(new_transaction)), 201


@bp.put("/transactions/<transaction_id>")
@jwt_required()
@database_operation(max_tries=3)
def update_transaction(transaction_id: int, session: Session):
    user_id = get_jwt_identity()
    transaction_data = request.json
    transaction_data["id"] = transaction_id
    updated_transaction = update_t(int(user_id), transaction_data, session)
    return jsonify(Transaction.serialize(updated_transaction)), 200


@bp.patch("/transactions")
@jwt_required()
@database_operation(max_tries=3)
def batch_updates_transactions(session: Session):
    user_id = get_jwt_identity()
    data = request.json
    transactions_data = data.get("transactions", None)
    if transactions_data:
        patched_transactions = [
            patch_transaction(int(user_id), transaction_data, session)
            for transaction_data in transactions_data
        ]

        return (
            jsonify({"transactions": Transaction.serialize_many(patched_transactions)}),
            200,
        )
    else:
        return 400


@bp.delete("/transactions/<transaction_id>")
@jwt_required()
@database_operation(max_tries=3)
def delete_transaction(transaction_id: int, session: Session):
    user_id = get_jwt_identity()
    delete_t(int(user_id), int(transaction_id), session)
    return {}, 204


@bp.post("/upload")
@jwt_required()
@database_operation(max_tries=3)
def upload_transaction(session: Session):
    transaction = request.files
    user_id = get_jwt_identity()
    account_id = request.form.get("account_id")

    if not account_id:
        return Response("No account id information found in the request", 400)

    if "file" not in transaction:
        return Response("Transaction file data not received", 400)

    file = transaction["file"]
    transaction_file_loader = TransactionFileLoader(
        file=file,
        user_id=int(user_id),
        account_id=int(account_id),
        session=session,
    )

    try:
        transaction_file_loader.process()
    except Exception as e:
        logger.error(e)
        return Response("Error while loading the transaction file", 400)

    return jsonify({"success": True}), 201
