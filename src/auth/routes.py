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
    # Only allow a sign-in redirect to another page on this same website.
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
    # US1: Authenticate users and send them to the home page for their role.
    # Check the login form, find the account, and sign the person in.
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            target = request.args.get("next")
            # Return to the page they first asked for if it is safe.
            if _is_safe_redirect_target(target):
                return redirect(target)
            # Otherwise, send them to the right home page for their role.
            if user.role == "Vendor":
                return redirect(url_for("vendor_home"))
            return redirect(url_for("student_home"))
        # Do not say whether the email or password was the wrong part.
        flash("Invalid email or password")
    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # US1: Register students and vendors with unique emails and hashed passwords.
    # TODO (US1): Add tests for duplicate emails, missing fields, and rejected passwords.
    # Create an account only after all the form answers pass their checks.
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
                # Save the new account; the database also protects email uniqueness.
                db.session.commit()
            except IntegrityError:
                # Undo a failed save and show a useful message.
                db.session.rollback()
                form.email.errors.append("Email is already registered.")
            else:
                flash("Registration successful! Please log in.")
                return redirect(url_for("auth.login"))
    return render_template("Register.html", form=form)


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    # Sign the person out only after they submit the logout form.
    form = LogoutForm()
    if form.validate_on_submit():
        logout_user()
        flash("You have been logged out.")
        return redirect(url_for("auth.login"))
    return render_template("logout.html", form=form)
