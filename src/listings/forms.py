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
    # Use the campus's chosen time zone for pickup times.
    return ZoneInfo(current_app.config.get("CAMPUS_TZ", "UTC"))


def to_utc(naive_dt):
    """Interpret a form datetime in campus local time and return UTC."""
    # Change campus time into one shared clock used to store dates.
    return naive_dt.replace(tzinfo=campus_tz()).astimezone(timezone.utc)


class MultiCheckboxField(SelectMultipleField):
    # Show each dietary choice as a check box.
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class ListingForm(FlaskForm):
    # US2: Validate listing details, portion limits, and pickup window.
    # Collect the food details vendors enter when posting a listing.
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
        # Make sure the pickup window is in the right order and still in the future.
        if not self.pickup_start.data or not field.data:
            return

        start = to_utc(self.pickup_start.data)
        end = to_utc(field.data)
        if end <= start:
            raise ValidationError("Pickup window must end after it starts")
        if end <= datetime.now(timezone.utc):
            raise ValidationError("Pickup window end cannot be in the past")


class ReservationForm:
    # TODO (US4): Define validation for reserving one or two portions.
    pass


class ListingEditForm:
    # TODO (US5): Define listing edit fields and reuse the US2 listing validation rules.
    pass


class PickupCodeForm:
    # TODO (US7): Define validation for a six-character pickup code.
    pass


class DashboardDateRangeForm:
    # TODO (US9): Define and validate a dashboard date range.
    pass


class RatingForm:
    # TODO (US10): Define a 1-5 star rating and optional comment up to 300 characters.
    pass
