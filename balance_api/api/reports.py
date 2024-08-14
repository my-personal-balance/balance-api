import enum

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm.session import Session

from balance_api.data.db import database_operation
from balance_api.data.dtos.tags import Tag
from balance_api.data.models.transactions import (
    list_group_by_tag,
    get_montly_balance,
    PeriodType,
)

bp = Blueprint("reports", __name__)


class ReportType(enum.Enum):
    group_by_tag = "group_by_tag"


@bp.get("/reports/transactions")
@jwt_required()
@database_operation(max_tries=3)
def get_transactions(session: Session = None):
    user_id = get_jwt_identity()
    report_type = request.args.get("report_type", type=ReportType)
    account_id = request.args.get("account_id", type=int)
    tag_id = request.args.get("tag_id", type=int)
    period_type = request.args.get("period_type", type=PeriodType)
    period_offset = request.args.get("period_offset", type=int)
    start_date = request.args.get("start_date", type=str)
    end_date = request.args.get("end_date", type=str)

    if report_type:
        if ReportType(report_type) == ReportType.group_by_tag:
            items = list_group_by_tag(
                user_id=user_id,
                account_id=account_id,
                tag_id=tag_id,
                period_type=period_type,
                period_offset=period_offset,
                start_date=start_date,
                end_date=end_date,
                session=session,
            )

            for item in items:
                item["tag"] = Tag.serialize(item["tag"]) if item["tag"] else None

            return jsonify({"items": items}), 200


@bp.get("/reports/trends")
@jwt_required()
@database_operation(max_tries=3)
def get_trends(session: Session = None):
    user_id = get_jwt_identity()
    account_id = request.args.get("account_id", type=int)
    tag_id = request.args.get("tag_id", type=int)

    items = get_montly_balance(
        user_id=user_id,
        account_id=account_id,
        tag_id=tag_id,
        session=session,
    )

    return jsonify({"items": items}), 200
