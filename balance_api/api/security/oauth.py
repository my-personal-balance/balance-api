from sqlalchemy.orm.session import Session
from flask import jsonify
from balance_api.api import security
from balance_api.api import Resource
from balance_api.connection.db import database_operation

from balance_api.models.users import authenticate


class AuthResource(Resource):
    fields = [
        "email",
        "password",
    ]

    protected_fields = []

    @classmethod
    def deserialize(cls, auth_data: dict, create=True) -> dict:
        auth_resource = {}

        for field in cls.fields:
            auth_resource[field] = auth_data.get(field, None)
        for field in cls.protected_fields:
            auth_resource.pop(field, None)

        return auth_resource


@database_operation(max_tries=3)
def token(session: Session, **auth):
    auth_resource = AuthResource.deserialize(auth["body"], create=True)
    user = authenticate(auth_resource.get("email"), auth_resource.get("password"), session)
    if user:
        jwt_token = security.generate_token(user)
        response = {
            "accessToken": jwt_token,
        }

        return jsonify(response), 200
    else:
        return 401


