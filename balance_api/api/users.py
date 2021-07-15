from flask import jsonify
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.session import Session

from balance_api.api import Resource
from balance_api.connection.db import database_operation
from balance_api.models.users import User


class UserResource(Resource):
    fields = [
        "id",
        "name",
        "email",
    ]

    protected_fields = [
        "created_at",
        "updated_at",
    ]

    def serialize(self) -> dict:
        resource = super().serialize()
        user: User = self.instance

        resource.update(
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            }
        )

        return resource

    @classmethod
    def deserialize(cls, user_data: dict, create=True) -> dict:
        user_resource = {}

        for field in cls.fields:
            user_resource[field] = user_data.get(field, None)
        for field in cls.protected_fields:
            user_resource.pop(field, None)

        return user_resource


@database_operation(max_tries=3)
def me(session: Session, **kwargs):
    user_id = dict(kwargs)["user"]
    q = session.query(User).filter(User.id == user_id)
    try:
        user = q.one()
        return jsonify(UserResource(user).serialize())
    except NoResultFound:
        return None


@database_operation(max_tries=3)
def create_user(session: Session, **user):
    user_resource = UserResource.deserialize(user["body"], create=True)
    new_user = User(**user_resource)
    session.add(new_user)
    session.commit()

    return jsonify(UserResource(new_user).serialize()), 201
