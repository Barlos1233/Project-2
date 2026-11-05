from datetime import datetime, timezone
from flask_login import current_user, login_required

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from decorators import vendor_required
from extensions import db
from models import DIETARY_TAGS, Listing
from .forms import ListingForm, to_utc


listings_bp = Blueprint("listings", __name__, url_prefix="/listings")


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
            pickup_location=form.pickup_location.data.strip(),
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


@listings_bp.get("/")
@login_required
def browse_listings():
    now = datetime.now(timezone.utc)
    selected_tags = request.args.getlist("tag")
    selected_location = request.args.get("location", "").strip()

    if any(tag not in DIETARY_TAGS for tag in selected_tags):
        abort(400, description="Choose valid dietary tags.")

    # Begin with the available listings.
    query = Listing.query.filter(
        Listing.pickup_end > now,
        Listing.portions > 0,
    )

    # A listing must contain every selected tag.
    if selected_tags:
        query = query.filter(
            Listing.dietary_tags.contains(selected_tags)
        )

    if selected_location:
        query = query.filter(
            Listing.pickup_location == selected_location
        )

    listings = query.order_by(Listing.pickup_end.asc()).all()

    # Build the dropdown from existing pickup locations.
    location_rows = (
        Listing.query.with_entities(Listing.pickup_location)
        .distinct()
        .order_by(Listing.pickup_location.asc())
        .all()
    )

    return render_template(
        "browse_listings.html",
        listings=listings,
        dietary_tags=DIETARY_TAGS,
        locations=[row[0] for row in location_rows],
        selected_tags=selected_tags,
        selected_location=selected_location,
    )


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
    pass


def cancel_reservation(reservation_id):
    # TODO (US6): Cancel an eligible active reservation and release its portions.
    pass


def confirm_pickup(listing_id):
    # TODO (US7): Validate the code, listing ownership, reservation status, and pickup window.
    pass


def vendor_dashboard():
    # TODO (US9): Calculate listing, portion, pickup, and no-show metrics for a vendor date range.
    pass


def rate_reservation(reservation_id):
    # TODO (US10): Allow a student to rate their picked-up reservation once.
    pass
