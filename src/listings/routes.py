from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user

from decorators import vendor_required
from extensions import db
from models import Listing
from .forms import ListingForm, to_utc


listings_bp = Blueprint("listings", __name__, url_prefix="/listings")


@listings_bp.route("/new", methods=["GET", "POST"])
@vendor_required
def post_listing():
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
    listings = (
        Listing.query.filter_by(vendor_id=current_user.id)
        .order_by(Listing.created_at.desc())
        .all()
    )
    return render_template("my_listings.html", listings=listings)
