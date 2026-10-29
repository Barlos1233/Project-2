from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    email = StringField(
        "Email", validators=[DataRequired(), Email(), Length(max=255)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8)]
    )
    role = SelectField(
        "Role",
        choices=[("", "Select role"), ("Student", "Student"), ("Vendor", "Vendor")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Register")
