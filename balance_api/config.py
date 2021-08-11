"""
 Application configuration variables
"""

import os

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USERNAME = os.getenv("DB_USER", "balance")
DB_PASSWORD = os.getenv("DB_PWD", "passw0rd")
DB_NAME = os.getenv("DB_NAME", "balance")

SQLALCHEMY_DATABASE_URI = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}",
)
SQLALCHEMY_RECORD_QUERIES = (
    os.getenv("SQLALCHEMY_RECORD_QUERIES", "true").lower() == "true"
)

RSA256_PRIVATE_CERT_PATH = os.getenv("RSA256_CERT_PATH", ".ssh/id_rsa")
RSA256_PUB_CERT_PATH = os.getenv("RSA256_CERT_PATH", ".ssh/id_rsa.pub")
