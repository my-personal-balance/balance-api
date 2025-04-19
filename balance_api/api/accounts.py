from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm.session import Session

from balance_api.data.db import database_operation
from balance_api.data.dtos.accounts import Account
from balance_api.data.models.accounts import (
    find_account as find_a,
    list_accounts as list_a,
    create_account as create_a,
    delete_account as delete_a,
)
from balance_api.data.models.transactions import get_balance, PeriodType

bp = Blueprint("accounts", __name__)


@bp.get("/accounts/<account_id>")
@jwt_required()
@database_operation(max_tries=3)
def find_account(account_id: int, session: Session):
    user_id = get_jwt_identity()
    account = find_a(int(user_id), int(account_id), session)
    if not account:
        return {}, 404

    account_resource = get_account_financial_data(account, session)
    return jsonify(account_resource)


@bp.get("/accounts")
@jwt_required()
@database_operation(max_tries=3)
def list_accounts(session: Session):
    user_id = get_jwt_identity()
    accounts = []
    for account in list_a(int(user_id), session):
        account_resource = get_account_financial_data(account, session)
        accounts.append(account_resource)

    return jsonify({"accounts": accounts})


def get_account_financial_data(account: Account, session: Session) -> dict:
    balance, incomes, expenses = get_balance(
        user_id=account.user_id, account_id=account.id, session=session
    )

    return Account.serialize(
        account,
        **{
            "balance": balance,
            "incomes": incomes,
            "expenses": expenses,
        }
    )


@bp.post("/accounts")
@jwt_required()
@database_operation(max_tries=3)
def create_account(session: Session):
    user_id = get_jwt_identity()
    account_resource = request.json | {"user_id": int(user_id)}
    new_account = create_a(account_resource, session)
    return jsonify(Account.serialize(new_account)), 201


@bp.delete("/accounts/<account_id>")
@jwt_required()
@database_operation(max_tries=3)
def delete_account(account_id: int, session: Session):
    user_id = get_jwt_identity()
    delete_a(int(user_id), int(account_id), session)
    return {}, 204


@bp.get("/balance")
@jwt_required()
@database_operation(max_tries=3)
def get_account_balance(session: Session):
    user_id = get_jwt_identity()
    account_id = request.args.get("account_id", type=int)
    tag_id = request.args.get("tag_id", type=int)
    period_type = request.args.get("period_type", type=PeriodType)
    period_offset = request.args.get("period_offset", type=int)
    start_date = request.args.get("start_date", type=str)
    end_date = request.args.get("end_date", type=str)

    period_type = period_type if period_type else PeriodType.CURRENT_MONTH.value

    balance, incomes, expenses = get_balance(
        int(user_id),
        account_id,
        tag_id,
        period_type,
        period_offset,
        start_date,
        end_date,
        session,
    )

    return jsonify(
        {
            "balance": balance,
            "incomes": incomes,
            "expenses": expenses,
        }
    )
