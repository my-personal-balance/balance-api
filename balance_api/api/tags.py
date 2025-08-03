from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm.session import Session

from balance_api.data.dtos.tags import Tag
from balance_api.data.db import database_operation
from balance_api.services.tags import TagService

bp = Blueprint("tags", __name__)


@bp.get("/tags/<tag_id>")
@jwt_required()
@database_operation(max_tries=3)
def find_tag(tag_id: int, session: Session):
    user_id = get_jwt_identity()
    tag_service = TagService(session)
    tag = tag_service.find_tag(int(user_id), tag_id, session)
    if tag:
        return jsonify(Tag.serialize(tag))
    return {}, 404


@bp.get("/tags")
@jwt_required()
@database_operation(max_tries=3)
def list_tags(session: Session):
    user_id = get_jwt_identity()
    tag_service = TagService(session)
    tags = tag_service.list_tags(int(user_id))
    return jsonify({"tags": Tag.serialize_many(tags)})
