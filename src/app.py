import os
from zoneinfo import ZoneInfo

import click
from flask import Flask, abort, jsonify, render_template
from flask_login import current_user, login_required
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text

from auth.routes import auth_bp
from extensions import db, login_manager
from listings.routes import listings_bp
from models import Location
from reservations.routes import reservations_bp


CAMPUS_LOCATIONS = [
    "Student Union",
    "Library",
    "Engineering Building",
    "Dorms North",
]
csrf = CSRFProtect()


def create_app():
    # Build the Flask app and read its private settings from the environment.
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["CAMPUS_TZ"] = os.environ.get("CAMPUS_TZ", "UTC")

    # Connect the database, sign-in helper, and page groups to this app.
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(listings_bp)
    app.register_blueprint(reservations_bp)

    # Make sure the database tables exist before the app starts serving pages.
    with app.app_context():
        db.create_all()

    @app.cli.command("seed-locations")
    def seed_locations():
        for name in CAMPUS_LOCATIONS:
            if not Location.query.filter_by(name=name).first():
                db.session.add(Location(name=name))
        db.session.commit()
        click.echo("Locations seeded")

    @app.template_filter("campus_time")
    def campus_time(dt):
        if dt is None:
            return ""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        tz = ZoneInfo(app.config.get("CAMPUS_TZ", "UTC"))
        return dt.astimezone(tz).strftime("%a %b %d, %I:%M %p")

    # Keep the short login links working alongside the /auth links.
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
        # Tell a visitor that the app is running.
        return jsonify(name="CampusEats", status="running")

    @app.get("/healthz")
    def health():
        # Ask the database a tiny question to check that it is reachable.
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ok")

    @app.get("/student/home")
    @login_required
    def student_home():
        # Only students should see the student home page.
        if current_user.role != "Student":
            abort(403)
        from auth.forms import LogoutForm

        return render_template(
            "student_home.html", user=current_user, form=LogoutForm()
        )

    @app.get("/vendor/home")
    @login_required
    def vendor_home():
        # Only vendors should see the vendor home page.
        if current_user.role != "Vendor":
            abort(403)
        from auth.forms import LogoutForm

        return render_template(
            "vendor_home.html", user=current_user, form=LogoutForm()
        )

    @app.errorhandler(403)
    def forbidden(error):
        # Show a friendly page when someone tries to open a page they cannot use.
        return render_template("403.html"), 403

    return app


# Create the app object that Flask runs.
app = create_app()
