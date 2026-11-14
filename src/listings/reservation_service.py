import secrets
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Listing, Reservation

# US4: Pickup codes skip look-alike characters (0/O, 1/I) so they are easy to read aloud.
CODE_CHARACTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 6


class ReservationError(Exception):
    """A reservation was refused. The message is safe to show to the student."""


def make_pickup_code():
    # Make random 6-character codes until we find one nobody has used.
    while True:
        code = "".join(secrets.choice(CODE_CHARACTERS) for _ in range(CODE_LENGTH))
        taken = db.session.execute(
            db.select(Reservation.id).where(Reservation.pickup_code == code)
        ).first()
        if taken is None:
            return code


def reserve(student_id, listing_id, portions):
    # US4: Reserve 1 or 2 portions for a student, or raise ReservationError.
    if portions not in (1, 2):
        raise ReservationError("Choose 1 or 2 portions.")

    # Lock this listing's row. If two students reserve at the same moment, the
    # second one waits here until the first has finished, so the last portion
    # can only be taken once.
    listing = db.session.execute(
        db.select(Listing)
        .where(Listing.id == listing_id)
        .with_for_update()
    ).scalar_one_or_none()

    if (
        listing is None
        or listing.is_cancelled
        or listing.pickup_end <= datetime.now(timezone.utc)
    ):
        db.session.rollback()
        raise ReservationError("This listing is not available.")

    # One active reservation per student per listing.
    already_reserved = db.session.execute(
        db.select(Reservation.id).where(
            Reservation.listing_id == listing_id,
            Reservation.student_id == student_id,
            Reservation.status == "active",
        )
    ).first()
    if already_reserved is not None:
        db.session.rollback()
        raise ReservationError("You already have a reservation for this listing.")

    if portions > listing.portions_available:
        db.session.rollback()
        raise ReservationError("Not enough portions left.")

    listing.portions_available -= portions
    reservation = Reservation(
        listing_id=listing_id,
        student_id=student_id,
        portions=portions,
        pickup_code=make_pickup_code(),
    )
    db.session.add(reservation)
    try:
        db.session.commit()  # saving also releases the lock
    except IntegrityError:
        db.session.rollback()
        raise ReservationError("Could not save your reservation. Please try again.")
    return reservation
