from datetime import datetime, timedelta, timezone

from extensions import db
from models import Listing, Location, User


DEMO_PASSWORD = "CampusEats123!"


def seed_demo_data():
    """Create demo accounts and first-start listings without resetting data."""
    try:
        vendor = User.query.filter_by(email="demo.vendor@example.com").first()
        student = User.query.filter_by(email="demo.student@example.com").first()

        if vendor is not None and vendor.role != "Vendor":
            raise RuntimeError("The demo vendor email belongs to another role.")
        if student is not None and student.role != "Student":
            raise RuntimeError("The demo student email belongs to another role.")

        vendor_created = vendor is None
        if vendor_created:
            vendor = User(
                name="Demo Vendor",
                email="demo.vendor@example.com",
                role="Vendor",
            )
            vendor.set_password(DEMO_PASSWORD)
            db.session.add(vendor)

        if student is None:
            student = User(
                name="Demo Student",
                email="demo.student@example.com",
                role="Student",
            )
            student.set_password(DEMO_PASSWORD)
            db.session.add(student)

        # Only the initial creation of the demo vendor creates sample listings.
        if vendor_created:
            now = datetime.now(timezone.utc)
            samples = [
                (
                    "Demo: Vegan rice bowl", "Rice, beans, and vegetables.",
                    5, "Student Union", ["vegan", "gluten-free"],
                ),
                (
                    "Demo: Vegetarian pasta", "Pasta with tomato sauce.",
                    8, "Library", ["vegetarian"],
                ),
                (
                    "Demo: Lentil soup", "Lentils and vegetables.",
                    6, "Library", ["vegan", "gluten-free"],
                ),
            ]

            for title, description, portions, location_name, tags in samples:
                location = Location.query.filter_by(name=location_name).one()
                db.session.add(
                    Listing(
                        vendor=vendor,
                        title=title,
                        description=description,
                        portions=portions,
                        portions_available=portions,
                        location=location,
                        dietary_tags=tags,
                        pickup_start=now - timedelta(minutes=10),
                        pickup_end=now + timedelta(hours=24),
                    )
                )

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise