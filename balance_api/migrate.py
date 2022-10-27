import alembic.config

from balance_api import config


def migrate():
    db_uri = config.SQLALCHEMY_DATABASE_URI
    alembic.config.main(
        argv=["--raiseerr", "-x", f"db_uri={db_uri}", "upgrade", "head"]
    )


if __name__ == "__main__":
    migrate()
