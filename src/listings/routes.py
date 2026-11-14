from datetime import datetime, timezone

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import String, cast
from sqlalchemy.orm import joinedload

from decorators import vendor_required
from extensions import db
from models import FILTERABLE_TAGS, Listing, Location, Reservation
from .forms import ListingEditForm, ListingForm, campus_tz, to_utc
from .reservation_service import ReservationError, reserve
from .reserve_forms import ReserveForm


listings_bp = Blueprint("listings", __name__, url_prefix="/listings")


def _contains_tag(tag):
    if db.session.get_bind().dialect.name == "sqlite":
        return cast(Listing.dietary_tags, String).like(f'%"{tag}"%')
    return Listing.dietary_tags.contains([tag])


def _as_utc(value):
    # SQLite returns naive datetimes; treat them as UTC like the PostgreSQL values.
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@listings_bp.route("/new", methods=["GET", "POST"])
@vendor_required
def post_listing():
    # US2: Vendors create listings; form validation enforces listing and pickup-window rules.
    # TODO (US2): Add tests for required fields, portion boundaries, and dietary tags.
    # Show the form first; save a listing after the vendor submits valid answers.
    form = ListingForm()
    if form.validate_on_submit():
        listing = Listing(
            vendor_id=current_user.id,
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            portions=form.portions.data,
            portions_available=form.portions.data,
            location_id=form.location_id.data,
            dietary_tags=form.dietary_tags.data,
            pickup_start=to_utc(form.pickup_start.data),
            pickup_end=to_utc(form.pickup_end.data),
        )
        db.session.add(listing)
        db.session.commit()
        flash("Listing posted")
        return redirect(url_for("listings.my_listings"))
    return render_template("post_listing.html", form=form)


@listings_bp.get("/mine")
@vendor_required
def my_listings():
    # Show only this vendor's listings, with locations ready for the template.
    listings = (
        Listing.query.filter_by(vendor_id=current_user.id)
        .options(joinedload(Listing.location))
        .order_by(Listing.created_at.desc())
        .all()
    )
    # Compute the visible status from cancellation and the listing's pickup end.
    now = datetime.now(timezone.utc)
    statuses = {
        listing.id: (
            "cancelled"
            if listing.is_cancelled
            else "ended"
            if _as_utc(listing.pickup_end) <= now
            else "active"
        )
        for listing in listings
    }
    return render_template(
        "my_listings.html", listings=listings, statuses=statuses
    )


@listings_bp.get("/")
@login_required
def browse_listings():
    selected_tags = [
        tag for tag in request.args.getlist("tags") if tag in FILTERABLE_TAGS
    ]
    nut_free = request.args.get("nut_free") == "1"
    location_id = request.args.get("location", type=int)
    page = request.args.get("page", 1, type=int)

    query = Listing.query.filter(
        Listing.pickup_end > datetime.now(timezone.utc),
        Listing.portions_available > 0,
        Listing.is_cancelled.is_(False),
    )
    if selected_tags:
        query = query.filter(*(_contains_tag(tag) for tag in selected_tags))
    if nut_free:
        query = query.filter(~_contains_tag("contains nuts"))
    if location_id:
        query = query.filter(Listing.location_id == location_id)

    pagination = query.order_by(Listing.pickup_start).paginate(
        page=page, per_page=12, error_out=False
    )

    return render_template(
        "browse_listings.html",
        pagination=pagination,
        locations=Location.query.order_by(Location.name).all(),
        tag_choices=FILTERABLE_TAGS,
        selected_tags=selected_tags,
        nut_free=nut_free,
        location_id=location_id,
        reserve_form=ReserveForm(),
    )


@listings_bp.post("/<int:listing_id>/reserve")
@login_required
def reserve_listing(listing_id):
    # US4: A student reserves 1 or 2 portions and receives a unique pickup code.
    if current_user.role != "Student":
        abort(403)

    form = ReserveForm()
    if not form.validate_on_submit():
        flash("Choose 1 or 2 portions.")
        return redirect(url_for("listings.browse_listings"))

    try:
        reservation = reserve(current_user.id, listing_id, form.portions.data)
    except ReservationError as error:
        flash(str(error))
        return redirect(url_for("listings.browse_listings"))

    return render_template("reservation_confirmation.html", reservation=reservation)


@listings_bp.route("/<int:listing_id>/edit", methods=["GET", "POST"])
@vendor_required
def edit_listing(listing_id):
    # Lock saves against concurrent reservations; ownership is part of the lookup.
    listing_query = Listing.query.filter_by(
        id=listing_id, vendor_id=current_user.id
    )
    if request.method == "POST":
        listing_query = listing_query.with_for_update()
    listing = listing_query.first_or_404()
    if listing.is_cancelled:
        flash("A cancelled listing cannot be edited.", "error")
        return redirect(url_for("listings.my_listings"))

    form = ListingEditForm(obj=listing)
    if request.method == "GET":
        # Date/time inputs use campus-local time while the database stores UTC.
        for field in (form.pickup_start, form.pickup_end):
            stored_time = getattr(listing, field.name)
            if stored_time.tzinfo is None:
                stored_time = stored_time.replace(tzinfo=timezone.utc)
            field.data = stored_time.astimezone(campus_tz()).replace(tzinfo=None)

    if form.validate_on_submit():
        reserved = listing.portions_reserved
        if form.portions.data < reserved:
            form.portions.errors.append(
                f"Portions cannot be less than the {reserved} already reserved."
            )
        else:
            # Keep available portions aligned with the edited total and reservations.
            listing.title = form.title.data.strip()
            listing.description = form.description.data.strip()
            listing.portions = form.portions.data
            listing.portions_available = form.portions.data - reserved
            listing.location_id = form.location_id.data
            listing.dietary_tags = form.dietary_tags.data
            listing.pickup_start = to_utc(form.pickup_start.data)
            listing.pickup_end = to_utc(form.pickup_end.data)
            db.session.commit()
            flash("Listing updated.", "success")
            return redirect(url_for("listings.my_listings"))

    return render_template("edit_listing.html", form=form, listing=listing)


@listings_bp.post("/<int:listing_id>/cancel")
@vendor_required
def cancel_listing(listing_id):
    # Lock the listing so a concurrent reservation cannot slip in during cancellation.
    listing = (
        Listing.query.filter_by(id=listing_id, vendor_id=current_user.id)
        .with_for_update()
        .first_or_404()
    )
    if listing.is_cancelled:
        flash("This listing is already cancelled.", "error")
        return redirect(url_for("listings.my_listings"))

    active_reservations = (
        Reservation.query.filter_by(listing_id=listing.id, status="active")
        .with_for_update()
        .all()
    )
    # Cancel active holds and return their portions before hiding the listing.
    listing.portions_available += sum(
        reservation.portions for reservation in active_reservations
    )
    for reservation in active_reservations:
        reservation.status = "cancelled"
    listing.is_cancelled = True
    db.session.commit()
    flash("Listing cancelled.", "success")
    return redirect(url_for("listings.my_listings"))


@listings_bp.get("/<int:listing_id>")
@vendor_required
def listing_details(listing_id):
    # Load student identities with reservations, but only for the owning vendor.
    listing = Listing.query.filter_by(
        id=listing_id, vendor_id=current_user.id
    ).first_or_404()
    reservations = (
        Reservation.query.filter_by(listing_id=listing.id)
        .options(joinedload(Reservation.student))
        .order_by(Reservation.created_at)
        .all()
    )
    return render_template(
        "listing_details.html", listing=listing, reservations=reservations
    )


def my_reservations():
    # TODO (US6): Show the current student's reservations and their statuses.
    from sqlalchemy.orm import joinedload
    from models import Reservation

    return (
        Reservation.query.filter_by(student_id=current_user.id)
        .options(
            joinedload(Reservation.listing).joinedload(Listing.vendor),
            joinedload(Reservation.listing).joinedload(Listing.location),
        )
        .join(Listing)
        .order_by(Listing.pickup_start.desc())
        .all()
    )


def cancel_reservation(reservation_id):
    # TODO (US6): Cancel an eligible active reservation and release its portions.
    from models import Reservation

    reservation = (
        Reservation.query.filter_by(id=reservation_id, student_id=current_user.id)
        .with_for_update()
        .first_or_404()
    )
    listing = Listing.query.filter_by(id=reservation.listing_id).with_for_update().first_or_404()
    if not reservation.can_cancel:
        return False
    reservation.status = "cancelled"
    listing.portions_available += reservation.portions
    db.session.commit()
    return True


def confirm_pickup(listing_id):
    # TODO (US7): Validate the code, listing ownership, reservation status, and pickup window.
    pass


def vendor_dashboard():
    # TODO (US9): Calculate listing, portion, pickup, and no-show metrics for a vendor date range.
    pass


def rate_reservation(reservation_id):
    # TODO (US10): Allow a student to rate their picked-up reservation once.
    pass
