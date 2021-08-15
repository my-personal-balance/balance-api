from flask import jsonify
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

from balance_api.api import Resource
from balance_api.connection.db import database_operation
from balance_api.models.tags import Tag, list_tags as list_t


class TagResource(Resource):
    fields = [
        "id",
        "value",
        "user_id",
    ]

    protected_fields = [
        "created_at",
        "updated_at",
    ]

    def serialize(self) -> dict:
        resource = super().serialize()
        tag: Tag = self.instance

        resource.update(
            {
                "id": tag.id,
                "value": tag.value,
                "user_id": tag.user_id,
            }
        )

        return resource

    @classmethod
    def deserialize(cls, tag_data: dict, create=True) -> dict:
        tag_resource = {}

        for field in cls.fields:
            tag_resource[field] = tag_data.get(field, None)
        for field in cls.protected_fields:
            tag_resource.pop(field, None)

        return tag_resource


@database_operation(max_tries=3)
def find_tag(user: int, tag_id: int, session: Session):
    q = session.query(Tag).where(
        Tag.user_id == user,
        Tag.id == tag_id,
    )
    try:
        tag = q.one()
    except NoResultFound:
        return {}, 404

    return jsonify(TagResource(tag).serialize())


@database_operation(max_tries=3)
def list_tags(user: int, session: Session):
    tags = list_t(user_id=user, session=session)
    return jsonify({"tags": [TagResource(tag).serialize() for tag in tags]})
