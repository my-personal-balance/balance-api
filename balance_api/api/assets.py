from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm.session import Session

from balance_api.data.db import database_operation
from balance_api.data.models.assets import (
    search_assets as search_a,
)

bp = Blueprint("assets", __name__)


@bp.get("/assets")
@jwt_required()
@database_operation(max_tries=3)
def search_assets(session: Session):
    user_id = get_jwt_identity()
    keywords = request.args.get("keywords")
    assets = search_a(keywords, session)
    return jsonify(
        {
            "assets": [],
        }
    )
