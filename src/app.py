import hmac
import os
import re
import secrets

from flask import (Flask, jsonify, render_template,
                   request, redirect, url_for,
                   session, flash, abort)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(80), nullable=False)
    
    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # US1: Automatically creates missing database tables
    with app.app_context():
        db.create_all()
    
    # US1: Simple CSRF protection for forms
    def form_token():
        if "_csrf_token" not in session:
            session["_csrf_token"] = secrets.token_hex(32)
        return session["_csrf_token"]
    
    app.jinja_env.globals["form_token"] = form_token
    
    def valid_form_token(token):
        submitted = request.form.get("csrf_token", "")
        expected = session.get("csrf_token", "")
        return bool(expected) and hmac.compare_digest(submitted, expected)

    # existing homepage
    @app.get("/")
    def index():
        return jsonify(name="CampusEats", status="running")

    # existing database health check
    @app.get("/healthz")
    def health():
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ok")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        errors = {}
        
        if request.method == "POST":
            if not valid_form_token():
                abort(400)
                
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            role = request.form.get("role", "")
            
            # checks required fields
            if not name:
                errors["name"] = "Name is required."
                
            if not email:
                errors["email"] = "Email is required."
            elif not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
                errors["email"] = "Invalid email format."
            
            if not password:
                errors["password"] = "Password is required."
            elif len(password) < 8:
                errors["password"] = "Password must be at least 8 characters long."
            
            if not role:
                errors["role"] = "Role is required."
            elif role not in ("Student", "Vendor"):
                errors["role"] = "Role must be either 'Student' or 'Vendor'."
            
            if len(name) > 100:
                errors["name"] = "Name must be less than 100 characters."
            
            if len(email) > 255:
                errors["email"] = "Email must be less than 255 characters."
                
            # check if email already exists
            if "email" not in errors:
                existing_user = db.session.execute(
                    db.select(User).filter_by(email=email)
                ).scalar_one_or_none()
                
                if existing_user:
                    errors["email"] = "Email is already registered."
            
            # saves only when all fields are valid
            if not errors:
                new_user = User(
                    name=name,
                    email=email,
                    password_hash=generate_password_hash(password),
                    role=role
                )
                
                db.session.add(new_user)
                
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    errors["email"] = "Email is already registered."
                else:
                    flash("Registration successful! Please login.")
                    return redirect(url_for("login"))
                
        return render_template("register.html", errors=errors)
    
    # US1: Login page
    @app.route("/login", methods=["GET", "POST"])
    def login():
        errors = None
        
        if requested.method == "POST":
            if not valid_form_token():
                abort(400)
            
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            
            # A failed login must not leave a previous login active
            session.pop("user_id", None)
            
            if not email or not password: 
                error = "Email and password are required."
            else: 
                user = db.session.execute(
                    db.select(User).filter_by(email=email)
                ).scalar_one_or_none()
                
                if user and check_password_hash(user.password_hash, password):
                    session.clear()
                    session["user_id"] = user.id
                    
                    if user.role == "Student":
                        return redirect(url_for("student_home"))
                    elif user.role == "Vendor":
                        return redirect(url_for("vendor_home"))
                error = "Invalid email or password."
            return render_template("login.html", error=error)
        
        # US1: Student homepage
    @app.route("/student/home")
    def student_home():
        user_id = session.get("user_id")
        if user_id is None:
            return redirect(url_for("login"))
        user = db.session.get(User, user_id)
        
        if user is None:
            session.clear()
            return redirect(url_for("login"))
        
        if user.role != "Student":
            abort(403)
        return render_template("student_home.html", user=user)
    
    # US1: Vendor homepage
    @app.route("/vendor/home")
    def vendor_home():
        user_id = session.get("user_id")
        if user_id is None:
            return redirect(url_for("login"))
        user = db.session.get(User, user_id)
        
        if user is None:
            session.clear()
            return redirect(url_for("login"))
        
        if user.role != "Vendor":
            abort(403)
        return render_template("vendor_home.html", user=user)
    
    # US1: Logout 
    @app.route("/logout")
    def logout():
        if not valid_from_token():
            abort(400)
        
        session.clear()
        flash("You have been logged out.")
        return redirect(url_for("login"))
    
    return app


app = create_app()
