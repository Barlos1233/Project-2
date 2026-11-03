import os

from flask import Flask, abort, jsonify, render_template
from flask_login import current_user, login_required
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

    with app.app_context():
        db.create_all()

    app.add_url_rule(
        "/login",
        endpoint="login",
        view_func=app.view_functions["auth.login"],
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/register",
        endpoint="register",
        view_func=app.view_functions["auth.register"],
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        "/logout",
        endpoint="logout",
        view_func=app.view_functions["auth.logout"],
        methods=["GET", "POST"],
    )

    @app.get("/")
    def index():
        return jsonify(name="CampusEats", status="running")

    @app.get("/healthz")
    def health():
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ok")

    @app.get("/student/home")
    @login_required
    def student_home():
        if current_user.role != "Student":
            abort(403)
        from auth.forms import LogoutForm

        return render_template(
            "student_home.html", user=current_user, form=LogoutForm()
        )

    @app.get("/vendor/home")
    @login_required
    def vendor_home():
        if current_user.role != "Vendor":
            abort(403)
        from auth.forms import LogoutForm

        return render_template(
            "vendor_home.html", user=current_user, form=LogoutForm()
        )

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    return app


app = create_app()
