import time

import jwt
from cryptography.hazmat.primitives import serialization
from jwt.exceptions import (
    DecodeError,
    InvalidAlgorithmError,
)
from jwt.exceptions import ExpiredSignatureError
from werkzeug.exceptions import Unauthorized

from balance_api import config
from balance_api.models.users import User

JWT_ISSUER = "com.julianovidal.balance-api"

public_key = open(config.RSA256_PUB_CERT_PATH, "r").read()
pub_key = serialization.load_ssh_public_key(public_key.encode())

private_key = open(config.RSA256_PRIVATE_CERT_PATH, "r").read()
priv_key = serialization.load_ssh_private_key(private_key.encode(), password=None)

JWT_LIFETIME_SECONDS = 3600
JWT_ALGORITHM = "RS256"


def generate_token(user: User):
    timestamp = _current_timestamp()
    payload = {
        "iss": JWT_ISSUER,
        "iat": int(timestamp),
        "exp": int(timestamp + JWT_LIFETIME_SECONDS),
        "sub": str(user.id),
    }

    return jwt.encode(
        payload=payload,
        key=priv_key,
        algorithm=JWT_ALGORITHM,
    )


def decode_token(token):
    try:
        timestamp = _current_timestamp()
        decoded = jwt.decode(
            token,
            key=pub_key,
            algorithms=[
                JWT_ALGORITHM,
            ],
        )
        expiration_timestamp = decoded.get("exp", 0)
        if expiration_timestamp < timestamp:
            raise DecodeError

        return decoded
    except DecodeError:
        raise Unauthorized()
    except ExpiredSignatureError:
        raise Unauthorized()
    except InvalidAlgorithmError:
        raise Unauthorized()


def _current_timestamp() -> int:
    return int(time.time())
