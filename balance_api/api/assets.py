from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from balance_api.data.db import database_operation

bp = Blueprint("assets", __name__)


@bp.get("/assets")
@jwt_required()
@database_operation(max_tries=3)
def search_assets():
    return jsonify(
        {
            "assets": [],
        }
    )
