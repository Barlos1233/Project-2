from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy.orm import joinedload

from decorators import student_required
from extensions import db
from models import Listing, Reservation

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
