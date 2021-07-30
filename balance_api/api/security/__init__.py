import time

import six
from jose import JWTError, jwt
from jose.constants import Algorithms
from werkzeug.exceptions import Unauthorized

from balance_api.models.users import User

JWT_ISSUER = "com.julianovidal"
JWT_SECRET = {
    "kty": "oct",
    "kid": "018c0ae5-4d9b-471b-bfd6-eef314bc7037",
    "use": "sig",
    "alg": "HS256",
    "k": "hJtXIZ2uSN5kbQfbtTNWbpdmhkV8FJG-Onbc6mxCcYg",
}
JWT_LIFETIME_SECONDS = 3600
JWT_ALGORITHM = Algorithms.HS256


def generate_token(user: User):
    timestamp = _current_timestamp()
    payload = {
        "iss": JWT_ISSUER,
        "iat": int(timestamp),
        "exp": int(timestamp + JWT_LIFETIME_SECONDS),
        "sub": str(user.id),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    try:
        timestamp = _current_timestamp()
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        expiration_timestamp = decoded.get("exp", 0)
        if expiration_timestamp < timestamp:
            raise JWTError

        return decoded
    except JWTError as e:
        six.raise_from(Unauthorized, e)


def _current_timestamp() -> int:
    return int(time.time())
