from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from extensions import db
from forms import RegistrationForm
from models import User
from .forms import LoginForm, LogoutForm


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
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            target = request.args.get("next")
            if _is_safe_redirect_target(target):
                return redirect(target)
            if user.role == "Vendor":
                return redirect(url_for("vendor_home"))
            return redirect(url_for("student_home"))
        flash("Invalid email or password")
    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        if User.query.filter_by(email=email).first():
            form.email.errors.append("Email is already registered.")
        else:
            user = User(
                name=form.name.data.strip(),
                email=email,
                role=form.role.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                form.email.errors.append("Email is already registered.")
            else:
                flash("Registration successful! Please log in.")
                return redirect(url_for("auth.login"))
    return render_template("Register.html", form=form)


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    form = LogoutForm()
    if form.validate_on_submit():
        logout_user()
        flash("You have been logged out.")
        return redirect(url_for("auth.login"))
    return render_template("logout.html", form=form)
