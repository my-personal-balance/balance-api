import connexion
from flask_cors import CORS
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy

from balance_api import config


def create_app():
    connexion_app = connexion.FlaskApp(
        __name__,
        specification_dir="openapi/",
        options={"propagate_exceptions": True, "swagger_ui": False},
    )

    connexion_app.add_api("spec.yaml")

    flask_app = connexion_app.app
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    flask_app.config["SQLALCHEMY_RECORD_QUERIES"] = config.SQLALCHEMY_RECORD_QUERIES

    CORS(flask_app)

    compress = Compress()
    compress.init_app(flask_app)

    return connexion_app


app = create_app()
db = SQLAlchemy(app.app)


def main():
    app.run()
