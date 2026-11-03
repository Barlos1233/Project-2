import os

from flask import Flask, jsonify, render_template
from sqlalchemy import text

from auth.routes import auth_bp
from extensions import db, login_manager
from listings.routes import listings_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["CAMPUS_TZ"] = os.environ.get("CAMPUS_TZ", "UTC")

    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(listings_bp)

    @app.get("/")
    def index():
        return jsonify(name="CampusEats", status="running")

    @app.get("/healthz")
    def health():
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ok")

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    return app


app = create_app()
