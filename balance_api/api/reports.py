import enum

from flask import jsonify
from sqlalchemy.orm.session import Session

from balance_api.api.tags import TagResource
from balance_api.connection.db import database_operation
from balance_api.models.transactions import list_group_by_tag, get_montly_balance


class ReportType(enum.Enum):
    group_by_tag = "group_by_tag"


@database_operation(max_tries=3)
def get_transactions(
    user: int,
    report_type: ReportType,
    account_id: int = None,
    tag_id: int = None,
    period_type: int = None,
    period_offset: int = None,
    start_date: int = None,
    end_date: int = None,
    session: Session = None,
):
    if report_type:

        if ReportType(report_type) == ReportType.group_by_tag:
            items = list_group_by_tag(
                user_id=user,
                account_id=account_id,
                tag_id=tag_id,
                period_type=period_type,
                period_offset=period_offset,
                start_date=start_date,
                end_date=end_date,
                session=session,
            )

            for item in items:
                item["tag"] = (
                    TagResource(item["tag"]).serialize() if item["tag"] else None
                )

            return jsonify({"items": items}), 200


@database_operation(max_tries=3)
def get_trends(
    user: int,
    account_id: int = None,
    tag_id: int = None,
    session: Session = None,
):
    items = get_montly_balance(
        user_id=user,
        account_id=account_id,
        tag_id=tag_id,
        session=session,
    )

    return jsonify({"items": items}), 200
