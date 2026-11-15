from datetime import datetime, timedelta, timezone

import pytest

from conftest import login
from extensions import db
from models import Listing, Location, Reservation


FMT = "%Y-%m-%dT%H:%M"


@pytest.fixture(autouse=True)
def seed_locations(app):
    app.test_cli_runner().invoke(args=["seed-locations"])


def make_listing(vendor, title="Food offer", portions=4, available=None, end=None):
    now = datetime.now(timezone.utc)
    pickup_end = end or now + timedelta(hours=2)
    listing = Listing(
        vendor_id=vendor.id,
        title=title,
        description="Surplus food",
        portions=portions,
        portions_available=portions if available is None else available,
        location_id=Location.query.filter_by(name="Student Union").one().id,
        dietary_tags=[],
        pickup_start=pickup_end - timedelta(hours=1),
        pickup_end=pickup_end,
    )
    db.session.add(listing)
    db.session.commit()
    return listing


def reservation_for(listing, student, portions=2):
    reservation = Reservation(
        listing_id=listing.id,
        student_id=student.id,
        portions=portions,
        pickup_code="ABC234",
        status="active",
    )
    db.session.add(reservation)
    db.session.commit()
    return reservation


def edit_payload(location_id, portions=6, end_offset=3):
    # Form dates are entered in campus-local time; test configuration uses UTC.
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return {
        "title": "Updated food",
        "description": "Updated description",
        "portions": portions,
        "location_id": location_id,
        "dietary_tags": ["vegan"],
        "pickup_start": (now + timedelta(hours=1)).strftime(FMT),
        "pickup_end": (now + timedelta(hours=end_offset)).strftime(FMT),
        "submit": "Save changes",
    }


def test_my_listings_shows_status_and_portion_counts(client, vendor):
    make_listing(vendor, title="Active food", portions=5, available=2)
    ended = make_listing(
        vendor,
        title="Ended food",
        end=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    cancelled = make_listing(vendor, title="Cancelled food")
    cancelled.is_cancelled = True
    db.session.commit()

    login(client, vendor)
    response = client.get("/listings/mine")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Active food" in page and "Status: active" in page
    assert "3 portions reserved" in page and "2 portions remaining" in page
    assert "Ended food" in page and "Status: ended" in page
    assert "Cancelled food" in page and "Status: cancelled" in page
    assert ended.id


def test_edit_listing_updates_fields_and_reuses_listing_validation(client, vendor):
    listing = make_listing(vendor)
    location_id = Location.query.filter_by(name="Library").one().id
    login(client, vendor)

    response = client.post(
        f"/listings/{listing.id}/edit",
        data=edit_payload(location_id),
    )

    assert response.status_code == 302
    db.session.refresh(listing)
    assert listing.title == "Updated food"
    assert listing.portions == 6
    assert listing.portions_available == 6
    assert listing.location_id == location_id
    assert listing.dietary_tags == ["vegan"]

    invalid = edit_payload(location_id, end_offset=0)
    response = client.post(f"/listings/{listing.id}/edit", data=invalid)
    assert response.status_code == 200
    assert b"Pickup window must end after it starts" in response.data
    assert listing.title == "Updated food"


def test_edit_cannot_reduce_portions_below_reservations(client, vendor, student):
    listing = make_listing(vendor, portions=4, available=2)
    reservation_for(listing, student)
    login(client, vendor)

    response = client.post(
        f"/listings/{listing.id}/edit",
        data=edit_payload(listing.location_id, portions=1),
    )

    assert response.status_code == 200
    assert b"cannot be less than the 2 already reserved" in response.data
    db.session.refresh(listing)
    assert listing.portions == 4
    assert listing.portions_available == 2


def test_cancel_hides_listing_and_cancels_active_reservations(
    client, vendor, student
):
    listing = make_listing(vendor, portions=4, available=2)
    reservation = reservation_for(listing, student)
    login(client, vendor)

    response = client.post(f"/listings/{listing.id}/cancel")

    assert response.status_code == 302
    db.session.refresh(listing)
    db.session.refresh(reservation)
    assert listing.is_cancelled is True
    assert listing.portions_available == 4
    assert reservation.status == "cancelled"

    login(client, student)
    assert b"Food offer" not in client.get("/listings/").data
    client.post(f"/listings/{listing.id}/reserve", data={"portions": "1"})
    assert db.session.query(Reservation).filter_by(listing_id=listing.id).count() == 1


def test_reservations_are_visible_only_to_the_listing_vendor(
    client, vendor, student
):
    listing = make_listing(vendor)
    reservation_for(listing, student)
    login(client, vendor)

    response = client.get(f"/listings/{listing.id}")
    assert response.status_code == 200
    assert b"Student" in response.data
    assert b"2 portions" in response.data

    other_vendor = type(vendor)(
        name="Other Vendor", email="other@example.com", role="Vendor"
    )
    other_vendor.set_password("password123")
    db.session.add(other_vendor)
    db.session.commit()
    login(client, other_vendor)

    assert client.get(f"/listings/{listing.id}").status_code == 404
    assert client.get(f"/listings/{listing.id}/edit").status_code == 404
    assert client.post(f"/listings/{listing.id}/cancel").status_code == 404
