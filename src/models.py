import secrets
from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import column_property
from extensions import db, login_manager

CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
RESERVATION_STATUSES = ("active", "picked_up", "cancelled", "no_show")


def generate_pickup_code(length=6):
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(length))


def _as_utc_datetime(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)

DIETARY_TAGS = ["vegetarian", "vegan", "gluten-free", "halal", "contains nuts"]
FILTERABLE_TAGS = list(DIETARY_TAGS)

# US1: User accounts, role, and password hashing support registration and login.
# A user can be a student or vendor. Passwords are saved in a protected form.
class User(UserMixin,db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("Student", "Vendor", name="user_role"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def set_password(self, password):
        # Turn the password into a protected code before saving it.
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Check a typed password against the protected saved code.
        return check_password_hash(self.password_hash, password)

class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

@login_manager.user_loader
def load_user(user_id):
    # Find the signed-in person's account using its number.
    return db.session.get(User, int(user_id))


# US2: Listing fields store vendor-posted food, portions, location, tags, and pickup window.
# A listing is one offer of extra food from a vendor.
# "portions" is the TOTAL the vendor posted. It never changes when students reserve;
# use portions_remaining to see how many are still free (US4).
class Listing(db.Model):
    __tablename__ = "listings"

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    portions = db.Column(db.Integer, nullable=False)
<<<<<<< HEAD
    portions_available = db.Column(db.Integer, nullable=False, default=0)
=======
>>>>>>> 1889ee2 (US8 version2: bug fix for seed-locations)
    location_id = db.Column(
        db.Integer, db.ForeignKey("locations.id"), nullable=False, index=True
    )
    dietary_tags = db.Column(ARRAY(db.String), nullable=False, default=list)
    pickup_start = db.Column(db.DateTime(timezone=True), nullable=False)
    pickup_end = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    vendor = db.relationship("User", backref="listings")
    location = db.relationship("Location")
<<<<<<< HEAD
    reservations = db.relationship(
        "Reservation", back_populates="listing", cascade="all, delete-orphan"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.portions is not None and self.portions_available is None:
            self.portions_available = self.portions
=======
>>>>>>> 1889ee2 (US8 version2: bug fix for seed-locations)

    # Keep the number of portions and the pickup times within safe limits.
    __table_args__ = (
        db.CheckConstraint("portions BETWEEN 1 AND 100", name="ck_portions_range"),
        db.CheckConstraint("portions_available BETWEEN 0 AND portions", name="ck_available_range"),
        db.CheckConstraint("pickup_end > pickup_start", name="ck_window_order"),
        db.Index("ix_listings_dietary_tags", "dietary_tags", postgresql_using="gin"),
    )

    @property
    def portions_remaining(self):
        # US4: Portions that no student has reserved yet.
        return self.portions - self.portions_reserved

# US4: A reservation is one student holding 1 or 2 portions of one listing.
# The pickup code is what the student shows the vendor at pickup (US7).
class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(
        db.Integer, db.ForeignKey("listings.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    student_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    portions = db.Column(db.Integer, nullable=False)
    pickup_code = db.Column(db.String(6), nullable=False, unique=True)
    status = db.Column(
        db.Enum(*RESERVATION_STATUSES, name="reservation_status"),
        nullable=False, default="active", server_default="active",
    )
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    listing = db.relationship("Listing", back_populates="reservations")
    student = db.relationship("User", backref="reservations")

    __table_args__ = (
        # A student can reserve 1 or 2 portions at a time.
        db.CheckConstraint("portions BETWEEN 1 AND 2", name="ck_reservation_portions"),
        # The database itself refuses a second active reservation for the same listing.
        db.Index(
            "uq_one_active_reservation", "listing_id", "student_id",
            unique=True, postgresql_where=db.text("status = 'active'"),
            sqlite_where=db.text("status = 'active'"),
        ),
    )

    @property
    def display_status(self):
        if (
            self.status == "active"
            and self.listing is not None
            and _as_utc_datetime(self.listing.pickup_end)
            <= datetime.now(timezone.utc)
        ):
            return "no_show"
        return self.status

    @property
    def can_cancel(self):
        return (
            self.status == "active"
            and self.listing is not None
            and _as_utc_datetime(self.listing.pickup_end) > datetime.now(timezone.utc)
        )


# US4: Total portions already taken on a listing (reservations that are not cancelled).
# Listing.portions_reserved can be used in queries and on a listing object.
Listing.portions_reserved = column_property(
    db.select(db.func.coalesce(db.func.sum(Reservation.portions), 0))
    .where(Reservation.listing_id == Listing.id, Reservation.status != "cancelled")
    .correlate_except(Reservation)
    .scalar_subquery()
)


class ListingCancellation:
    # TODO (US5): Define how a vendor's cancellation state is stored for a listing.
    pass


class Rating:
    # TODO (US10): Define a one-time rating and optional comment linked to a picked-up reservation.
    pass
