from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm.session import Session
from balance_api.data.db import database_operation
from balance_api.data.models.split_transactions import (
    create_split_transactions,
    list_split_transactions,
)
from balance_api.data.dtos.split_transactions import SplitTransaction

bp = Blueprint("split_transactions", __name__)


@bp.post("/transactions/<transaction_id>/split")
@jwt_required()
@database_operation(max_tries=3)
def split_transaction(transaction_id: int, session: Session):
    user_id = get_jwt_identity()
    split_transactions_data = request.json

    if "transactions" in split_transactions_data:
        create_split_transactions(
            user_id=int(user_id),
            transaction_id=int(transaction_id),
            split_transactions=split_transactions_data["transactions"],
            session=session,
        )

    split_transactions = list_split_transactions(
        user_id=int(user_id), transaction_id=int(transaction_id), session=session
    )

    return (
        jsonify(
            {
                "split_transactions": SplitTransaction.serialize_many(
                    split_transactions
                ),
            }
        ),
        200,
    )
