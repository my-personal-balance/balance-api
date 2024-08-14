from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm.session import Session

from balance_api.data.dtos.tags import Tag
from balance_api.data.db import database_operation
from balance_api.data.models.tags import (
    find_tag as find_t,
    list_tags as list_t,
)

bp = Blueprint("tags", __name__)


@bp.get("/tags/<tag_id>")
@jwt_required()
@database_operation(max_tries=3)
def find_tag(tag_id: int, session: Session):
    user_id = get_jwt_identity()
    tag = find_t(user_id, tag_id, session)
    if tag:
        return jsonify(Tag.serialize(tag))
    return {}, 404


@bp.get("/tags")
@jwt_required()
@database_operation(max_tries=3)
def list_tags(session: Session):
    user_id = get_jwt_identity()
    tags = list_t(user_id, session)
    return jsonify({"tags": Tag.serialize_many(tags)})
