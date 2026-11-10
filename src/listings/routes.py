from datetime import datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import String, cast

from decorators import vendor_required
from extensions import db
from models import FILTERABLE_TAGS, Listing, Location
from .forms import ListingForm, to_utc


listings_bp = Blueprint("listings", __name__, url_prefix="/listings")


def _contains_tag(tag):
    if db.session.get_bind().dialect.name == "sqlite":
        return cast(Listing.dietary_tags, String).like(f'%"{tag}"%')
    return Listing.dietary_tags.contains([tag])


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
    # US5: Existing starting point for the vendor's listing-management page.
    # TODO (US5): Show status and reservation counts; add edit, cancel, and reservation details.
    # Find this vendor's listings and show the newest ones first.
    listings = (
        Listing.query.filter_by(vendor_id=current_user.id)
        .order_by(Listing.created_at.desc())
        .all()
    )
    return render_template("my_listings.html", listings=listings)


# The following handlers are placeholders and are not registered as routes yet.
@listings_bp.get("/")
@login_required
def browse_listings():
    selected_tags = [
        tag for tag in request.args.getlist("tags") if tag in FILTERABLE_TAGS
    ]
    nut_free = request.args.get("nut_free") == "1"
    location_id = request.args.get("location", type=int)
    page = request.args.get("page", 1, type=int)

    query = Listing.query.filter(Listing.pickup_end > datetime.now(timezone.utc))
    query = query.filter(Listing.portions > 0)
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
    )
# us4


def reserve_listing(listing_id):
    # TODO (US4): Validate availability, prevent duplicate/over-capacity reservations, and issue a pickup code.
    pass


def edit_listing(listing_id):
    # TODO (US5): Edit a vendor-owned listing and prevent portions dropping below the reserved count.
    pass


def cancel_listing(listing_id):
    # TODO (US5): Cancel a vendor-owned listing and its active reservations.
    pass


def listing_details(listing_id):
    # TODO (US5): Show reservation names and portions for a vendor-owned listing.
    pass


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


def filter_listings():
    # TODO (US8): Apply all selected dietary tags and optional campus location to listings.
    pass


def vendor_dashboard():
    # TODO (US9): Calculate listing, portion, pickup, and no-show metrics for a vendor date range.
    pass


def rate_reservation(reservation_id):
    # TODO (US10): Allow a student to rate their picked-up reservation once.
    pass
