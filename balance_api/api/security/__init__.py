from flask_jwt_extended import create_access_token

from balance_api.data.models.users import User


def generate_token(user: User):
    access_token = create_access_token(user.id)
    return access_token
