import os

SQLALCHEMY_DATABASE_URI = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "postgresql://balance:passw0rd@127.0.0.1:5432/balance"
)
