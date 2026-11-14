# Shared helpers used by routes and models throughout the app.
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# These helpers are connected to the app when it starts.
db = SQLAlchemy()
login_manager = LoginManager()
# Send people who need to sign in to the login page.
login_manager.login_view = "auth.login"
