import enum

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm.session import Session

from balance_api.data.db import database_operation
from balance_api.services.auto_classify import AutoClassifyService

bp = Blueprint(name="auto-classify", import_name=__name__, url_prefix="/auto-classify")


@bp.post("/classify-transactions")
@jwt_required()
@database_operation(max_tries=3)
def classify_transactions(session: Session = None):
    user_id = get_jwt_identity()
    transactions = request.json.get("transactions", [])
    service = AutoClassifyService(session)
    response = service.classify(int(user_id), transactions)
    return jsonify(response), 200
