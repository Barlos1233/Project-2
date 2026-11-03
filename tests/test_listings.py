from datetime import datetime, timedelta

import pytest

from conftest import login
from extensions import db
from models import Listing


FMT = "%Y-%m-%dT%H:%M"
now = datetime.now()


def payload(start, end):
    return {
        "title": "Pasta night",
        "description": "Leftovers",
        "portions": 10,
        "pickup_location": "Union",
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
    login(client, vendor)

    response = client.post("/listings/new", data=payload(start, end))

    assert response.status_code == 200
    assert message in response.get_data(as_text=True)
    assert db.session.query(Listing).count() == 0


def test_valid_window_saved(client, vendor):
    login(client, vendor)

    response = client.post(
        "/listings/new",
        data=payload(now + timedelta(days=1), now + timedelta(days=1, hours=1)),
    )

    assert response.status_code == 302
    listing = db.session.query(Listing).one()
    assert listing.vendor_id == vendor.id


def test_student_denied_get(client, student):
    login(client, student)

    response = client.get("/listings/new")

    assert response.status_code == 403
    assert b"Only vendors can post listings." in response.data


def test_student_denied_post_and_nothing_saved(client, student):
    login(client, student)

    response = client.post(
        "/listings/new",
        data=payload(now + timedelta(days=1), now + timedelta(days=1, hours=1)),
    )

    assert response.status_code == 403
    assert db.session.query(Listing).count() == 0


def test_anonymous_redirected_to_login(client):
    response = client.get("/listings/new")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
