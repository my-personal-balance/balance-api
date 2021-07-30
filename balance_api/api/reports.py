from flask import jsonify
from sqlalchemy.orm.session import Session

from balance_api.connection.db import database_operation
from balance_api.models.transactions import get_daily_balance


@database_operation(max_tries=3)
def get_balance(
    account_id: int = None,
    period_type: int = None,
    period_offset: int = None,
    start_date: int = None,
    end_date: int = None,
    session: Session = None,
    **kwargs,
):
    user_id = dict(kwargs)["user"]

    balances = get_daily_balance(
        user_id=int(user_id),
        account_id=account_id,
        period_type=period_type,
        period_offset=period_offset,
        start_date=start_date,
        end_date=end_date,
        session=session,
    )

    balances2 = [
        {
            "date": balance[0],
            "amount": round(balance[1], 2) if balance[1] else None,
        }
        for balance in balances
    ]

    return jsonify({"balances": balances2}), 200
