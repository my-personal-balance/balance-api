from flask import Flask, jsonify
from flask_compress import Compress
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from balance_api.api import (
    accounts,
    reports,
    split_transactions,
    tags,
    transactions,
    users,
)
from balance_api.api.security import oauth
from balance_api.data.models import Base


def create_app():
    # create and configure the _app
    _app = Flask(__name__, instance_relative_config=False)
    _app.config.from_pyfile("config.py", silent=True)
    CORS(_app)

    compress = Compress()
    compress.init_app(_app)

    _app.register_blueprint(oauth.bp)
    _app.register_blueprint(accounts.bp)
    _app.register_blueprint(reports.bp)
    _app.register_blueprint(split_transactions.bp)
    _app.register_blueprint(tags.bp)
    _app.register_blueprint(transactions.bp)
    _app.register_blueprint(users.bp)

    # a simple page that says hello
    @_app.route("/hello")
    def hello():
        return "Hello, World!"

    return _app


app = create_app()
db = SQLAlchemy(app, model_class=Base)
jwt = JWTManager(app)

@jwt.user_identity_loader
def user_identity_lookup(user_id):
    return str(user_id)

@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    return jsonify({"msg": "Invalid token - {}".format(error_string)}), 401


def main():
    app.run()
