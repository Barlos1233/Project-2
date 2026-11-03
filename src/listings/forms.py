from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from wtforms.widgets import CheckboxInput, ListWidget

from models import DIETARY_TAGS


def campus_tz():
    return ZoneInfo(current_app.config.get("CAMPUS_TZ", "UTC"))


def to_utc(naive_dt):
    """Interpret a form datetime in campus local time and return UTC."""
    return naive_dt.replace(tzinfo=campus_tz()).astimezone(timezone.utc)


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class ListingForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[DataRequired()])
    portions = IntegerField(
        "Portions", validators=[DataRequired(), NumberRange(min=1, max=100)]
    )
    pickup_location = StringField(
        "Pickup location", validators=[DataRequired(), Length(max=255)]
    )
    dietary_tags = MultiCheckboxField(
        "Dietary tags",
        choices=[(tag, tag.title()) for tag in DIETARY_TAGS],
    )
    pickup_start = DateTimeLocalField(
        "Pickup window start",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()],
    )
    pickup_end = DateTimeLocalField(
        "Pickup window end",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()],
    )
    submit = SubmitField("Post")

    def validate_pickup_end(self, field):
        if not self.pickup_start.data or not field.data:
            return

        start = to_utc(self.pickup_start.data)
        end = to_utc(field.data)
        if end <= start:
            raise ValidationError("Pickup window must end after it starts")
        if end <= datetime.now(timezone.utc):
            raise ValidationError("Pickup window end cannot be in the past")
