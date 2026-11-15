from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from decorators import student_required
from extensions import db
from listings.forms import RatingForm
from models import Listing, Rating, Reservation

reservations_bp = Blueprint("reservations", __name__, url_prefix="/reservations")


@reservations_bp.get("/mine")
@student_required
def my_reservations():
    reservations = (
        Reservation.query.filter_by(student_id=current_user.id)
        .options(
            joinedload(Reservation.listing).joinedload(Listing.vendor),
            joinedload(Reservation.listing).joinedload(Listing.location),
        )
        .join(Listing)
        .order_by(Listing.pickup_start.desc())
        .all()
    )
    return render_template("my_reservations.html", reservations=reservations)


@reservations_bp.post("/<int:reservation_id>/cancel")
@student_required
def cancel(reservation_id):
    reservation = (
        Reservation.query.filter_by(id=reservation_id, student_id=current_user.id)
        .with_for_update()
        .first_or_404()
    )
    listing = Listing.query.filter_by(id=reservation.listing_id).with_for_update().first_or_404()

    if not reservation.can_cancel:
        db.session.rollback()
        flash("This reservation can no longer be cancelled.", "error")
        return redirect(url_for("reservations.my_reservations"))

    reservation.status = "cancelled"
    listing.portions_available += reservation.portions
    db.session.commit()

    flash("Reservation cancelled.", "success")
    return redirect(url_for("reservations.my_reservations"))


@reservations_bp.post("/<int:reservation_id>/rate")
@student_required
def rate(reservation_id):
    # US10: A student rates one of their own picked-up reservations, once.
    # Lock the reservation row so a double click cannot save two ratings.
    reservation = (
        Reservation.query.filter_by(id=reservation_id, student_id=current_user.id)
        .with_for_update()
        .first_or_404()
    )
    form = RatingForm()

    if reservation.status != "picked_up":
        error = "Only a picked-up reservation can be rated."
    elif reservation.rating is not None:
        error = "You have already rated this pickup."
    elif not form.validate_on_submit():
        error = "Choose 1 to 5 stars. A comment can be at most 300 characters."
    else:
        error = None

    if error:
        db.session.rollback()
        flash(error, "error")
        return redirect(url_for("reservations.my_reservations"))

    comment = (form.comment.data or "").strip() or None
    db.session.add(
        Rating(reservation_id=reservation.id, stars=form.stars.data, comment=comment)
    )
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("You have already rated this pickup.", "error")
        return redirect(url_for("reservations.my_reservations"))

    flash("Thanks for your rating.", "success")
    return redirect(url_for("reservations.my_reservations"))
