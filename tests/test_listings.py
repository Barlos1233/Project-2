from datetime import datetime, timedelta

import pytest

from conftest import login
from extensions import db
from models import Listing, Location


FMT = "%Y-%m-%dT%H:%M"
# Use a nearby time so test pickup windows are easy to set.
now = datetime.now()


@pytest.fixture(autouse=True)
def seed_locations(app):
    app.test_cli_runner().invoke(args=["seed-locations"])


def payload(start, end):
    # Build the answers a vendor would enter on the listing form.
    return {
        "title": "Pasta night",
        "description": "Leftovers",
        "portions": 10,
        "location_id": Location.query.filter_by(name="Student Union").one().id,
        "dietary_tags": ["vegan"],
        "pickup_start": start.strftime(FMT),
        "pickup_end": end.strftime(FMT),
    }


@pytest.mark.parametrize(
    "start,end,message",
    [
        (
            now + timedelta(days=2),
            now + timedelta(days=1),
            "must end after",
        ),
        (
            now + timedelta(days=1),
            now + timedelta(days=1),
            "must end after",
        ),
        (
            now - timedelta(days=2),
            now - timedelta(days=1),
            "cannot be in the past",
        ),
    ],
)
def test_invalid_window_not_saved(client, vendor, start, end, message):
    # Bad pickup times should show an error and should not save a listing.
    login(client, vendor)

    response = client.post("/listings/new", data=payload(start, end))

    assert response.status_code == 200
    assert message in response.get_data(as_text=True)
    assert db.session.query(Listing).count() == 0


def test_valid_window_saved(client, vendor):
    # A good pickup window should save a listing for the signed-in vendor.
    login(client, vendor)

    response = client.post(
        "/listings/new",
        data=payload(now + timedelta(days=1), now + timedelta(days=1, hours=1)),
    )

    assert response.status_code == 302
    listing = db.session.query(Listing).one()
    assert listing.vendor_id == vendor.id
    assert listing.location.name == "Student Union"
    assert listing.location_id == Location.query.filter_by(name="Student Union").one().id


def test_existing_location_is_reused(client, vendor):
    location = Location.query.filter_by(name="Student Union").one()
    login(client, vendor)

    response = client.post(
        "/listings/new",
        data=payload(now + timedelta(days=1), now + timedelta(days=1, hours=1)),
    )

    assert response.status_code == 302
    assert db.session.query(Listing).one().location_id == location.id


def test_student_denied_get(client, student):
    # A student should not be allowed to open the vendor listing form.
    login(client, student)

    response = client.get("/listings/new")

    assert response.status_code == 403
    assert b"Only vendors can post listings." in response.data


def test_student_denied_post_and_nothing_saved(client, student):
    # A student should not be able to save a listing by sending the form directly.
    login(client, student)

    response = client.post(
        "/listings/new",
        data=payload(now + timedelta(days=1), now + timedelta(days=1, hours=1)),
    )

    assert response.status_code == 403
    assert db.session.query(Listing).count() == 0


def test_anonymous_redirected_to_login(client):
    # A visitor who is not signed in should be sent to the login page.
    response = client.get("/listings/new")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
