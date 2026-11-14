from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    # Ask for the two details needed to sign in.
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class LogoutForm(FlaskForm):
    # Add a safe button for signing out.
    submit = SubmitField("Log out")
