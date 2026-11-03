from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user

from models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _is_safe_redirect_target(target):
    if (
        not target
        or "\\" in target
        or not target.startswith("/")
        or target.startswith("//")
    ):
        return False

    destination = urlsplit(target)
    return not destination.scheme and not destination.netloc


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            target = request.args.get("next")
            if _is_safe_redirect_target(target):
                return redirect(target)
            return redirect(url_for("listings.my_listings"))
        flash("Invalid email or password")
    return render_template("login.html")
