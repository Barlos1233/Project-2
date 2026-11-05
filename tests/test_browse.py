from datetime import datetime, timedelta, timezone
import html as html_lib
import re
from urllib.parse import parse_qs, urlparse

import pytest

from conftest import login
from extensions import db
from models import Listing, Location


def add_listing(vendor, location, tags, end_offset_hours=2, title="Food"):
    now = datetime.now(timezone.utc)
    listing = Listing(
        vendor_id=vendor.id,
        title=title,
        description="x",
        portions=5,
        location_id=location.id,
        dietary_tags=tags,
        pickup_start=now + timedelta(hours=end_offset_hours - 1),
        pickup_end=now + timedelta(hours=end_offset_hours),
    )
    db.session.add(listing)
    db.session.commit()
    return listing


@pytest.fixture
def setup(app, vendor, student, client):
    union, library = Location(name="Union"), Location(name="Library")
    db.session.add_all([union, library])
    db.session.commit()
    add_listing(vendor, union, ["vegan", "gluten-free"], title="Vegan GF Union")
    add_listing(vendor, union, ["vegetarian"], title="Veg Union")
    add_listing(vendor, library, ["vegan", "contains nuts"], title="Vegan Nuts Library")
    add_listing(vendor, union, ["vegan"], end_offset_hours=-1, title="Expired")
    login(client, student)
    return union, library


def listing_html(response):
    return response.get_data(as_text=True)


def test_seed_locations_command_is_idempotent(app):
    runner = app.test_cli_runner()

    first = runner.invoke(args=["seed-locations"])
    second = runner.invoke(args=["seed-locations"])

    assert first.exit_code == 0
    assert first.output.strip() == "Locations seeded"
    assert second.exit_code == 0
    assert Location.query.count() == 4
    assert {location.name for location in Location.query.all()} == {
        "Student Union",
        "Library",
        "Engineering Building",
        "Dorms North",
    }


def test_no_filters_shows_available_only(client, setup):
    html = listing_html(client.get("/listings/"))
    assert "Expired" not in html and "Veg Union" in html


def test_tag_filter_requires_all_tags(client, setup):
    html = listing_html(client.get("/listings/?tags=vegan&tags=gluten-free"))
    assert "Vegan GF Union" in html
    assert "Vegan Nuts Library" not in html


def test_invalid_tags_are_ignored(client, setup):
    html = listing_html(client.get("/listings/?tags=not-a-tag"))
    assert "Veg Union" in html
    assert "not-a-tag" not in html


def test_location_filter(client, setup):
    union, _ = setup
    html = listing_html(client.get(f"/listings/?location={union.id}"))
    assert "Veg Union" in html and "Vegan Nuts Library" not in html


def test_combined_filters(client, setup):
    union, _ = setup
    html = listing_html(client.get(f"/listings/?tags=vegan&location={union.id}"))
    assert "Vegan GF Union" in html and "Veg Union" not in html


def test_nut_free_excludes_nut_listings(client, setup):
    html = listing_html(client.get("/listings/?tags=vegan&nut_free=1"))
    assert "Vegan Nuts Library" not in html and "Vegan GF Union" in html


def test_no_matches_shows_empty_state(client, setup):
    assert "No food matches" in listing_html(client.get("/listings/?tags=halal"))


def test_pagination_carries_filter_values(client, vendor, student):
    location = Location(name="Union")
    db.session.add(location)
    db.session.commit()
    for index in range(13):
        add_listing(
            vendor,
            location,
            ["vegan"],
            end_offset_hours=2 + index,
            title=f"Vegan listing {index}",
        )
    login(client, student)

    first_page = client.get(
        f"/listings/?tags=vegan&location={location.id}&nut_free=1"
    )
    html = listing_html(first_page)
    next_href = html_lib.unescape(
        re.search(r'<a href="([^"]+)">Next</a>', html).group(1)
    )
    next_query = parse_qs(urlparse(next_href).query)

    assert next_query["tags"] == ["vegan"]
    assert next_query["location"] == [str(location.id)]
    assert next_query["nut_free"] == ["1"]

    second_page = client.get(next_href)
    assert "Vegan listing 12" in listing_html(second_page)
    assert "Vegan listing 0" not in listing_html(second_page)


def test_anonymous_redirected(app):
    assert app.test_client().get("/listings/").status_code == 302
