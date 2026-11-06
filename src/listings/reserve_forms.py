from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import InputRequired, NumberRange


# US4: The form a student submits to reserve portions. It also carries the CSRF token.
class ReserveForm(FlaskForm):
    portions = IntegerField(
        "Portions",
        validators=[InputRequired(), NumberRange(min=1, max=2)],
    )
