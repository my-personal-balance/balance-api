"""
 Application configuration variables
"""

import logging
import os

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="utf-8",
    level=logging.INFO,
)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USERNAME = os.getenv("DB_USER", "balance")
DB_PASSWORD = os.getenv("DB_PWD", "passw0rd")
DB_NAME = os.getenv("DB_NAME", "balance")

SQLALCHEMY_DATABASE_URI = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    f"postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}",
)
SQLALCHEMY_RECORD_QUERIES = (
    os.getenv("SQLALCHEMY_RECORD_QUERIES", "true").lower() == "true"
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret")
JWT_ACCESS_TOKEN_EXPIRES = 3600

# JWT_PRIVATE_KEY = os.getenv("RSA256_CERT_PATH", ".ssh/id_rsa")
# JWT_PUBLIC_KEY = os.getenv("RSA256_CERT_PATH", ".ssh/id_rsa.pub")
