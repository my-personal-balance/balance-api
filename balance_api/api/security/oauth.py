from flask import Blueprint, request, jsonify
from sqlalchemy.orm.session import Session

from balance_api.api import security
from balance_api.data.db import database_operation
from balance_api.data.models.users import authenticate

bp = Blueprint("oauth", __name__, url_prefix="/oauth2")


@bp.post("/token")
@database_operation(max_tries=3)
def token(session: Session):
    data = request.json
    user = authenticate(data.get("email"), data.get("password"), session)
    if user:
        jwt_token = security.generate_token(user)
        response = {
            "accessToken": jwt_token,
        }

        return jsonify(response), 200
    else:
        return jsonify({}), 401
