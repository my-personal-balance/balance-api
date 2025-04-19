from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm.session import Session

from balance_api.data.db import database_operation
from balance_api.data.dtos.users import User
from balance_api.data.models.users import find_user, create_user

bp = Blueprint("users", __name__)


@bp.get("/users")
@jwt_required()
@database_operation(max_tries=3)
def me(session: Session):
    user_id = get_jwt_identity()
    user = find_user(int(user_id), session)
    if user:
        return jsonify(User.serialize(user)), 200


@bp.post("/users")
@jwt_required()
@database_operation(max_tries=3)
def create_users(session: Session):
    user_resource = request.json
    user = create_user(user_resource, session)
    return jsonify(User.serialize(user)), 201
