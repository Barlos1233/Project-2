import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    @app.get("/")
    def index():
        return jsonify(name="CampusEats", status="running")

    @app.get("/healthz")
    def health():
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ok")

    return app


app = create_app()
