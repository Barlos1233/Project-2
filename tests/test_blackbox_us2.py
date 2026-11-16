import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_BLACKBOX") != "1",
    reason="Set RUN_BLACKBOX=1 to run the Docker Compose browser test.",
)


def _register_and_login(driver, wait, name, role):
    email = f"{uuid.uuid4().hex}@example.com"
    password = "campuseats-test-password"

    driver.get(f"{os.environ['BLACKBOX_BASE_URL']}/register")
    driver.find_element(By.NAME, "name").send_keys(name)
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    Select(driver.find_element(By.NAME, "role")).select_by_visible_text(role)
    driver.find_element(By.NAME, "submit").click()
    wait.until(EC.url_contains("/auth/login"))

    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "submit").click()
    wait.until(
        EC.url_contains(
            "/vendor/home" if role == "Vendor" else "/student/home"
        )
    )


def _fill_listing_form(driver, title, start, end):
    driver.find_element(By.NAME, "title").clear()
    driver.find_element(By.NAME, "title").send_keys(title)
    driver.find_element(By.NAME, "description").clear()
    driver.find_element(By.NAME, "description").send_keys(
        "Black-box test listing"
    )
    driver.find_element(By.NAME, "portions").clear()
    driver.find_element(By.NAME, "portions").send_keys("3")
    Select(driver.find_element(By.NAME, "location_id")).select_by_visible_text(
        "Student Union"
    )
    vegan = driver.find_element(
        By.CSS_SELECTOR, 'input[name="dietary_tags"][value="vegan"]'
    )
    if not vegan.is_selected():
        vegan.click()

    for field_name, value in (
        ("pickup_start", start),
        ("pickup_end", end),
    ):
        field = driver.find_element(By.NAME, field_name)
        driver.execute_script(
            """
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event("input", { bubbles: true }));
            arguments[0].dispatchEvent(new Event("change", { bubbles: true }));
            """,
            field,
            value.strftime("%Y-%m-%dT%H:%M"),
        )


def test_vendor_posts_listing_and_student_is_denied():
    driver = webdriver.Remote(
        command_executor=os.environ["SELENIUM_REMOTE_URL"],
        options=webdriver.ChromeOptions(),
    )
    wait = WebDriverWait(driver, 15)
    base_url = os.environ["BLACKBOX_BASE_URL"]

    try:
        title = f"Browser test {uuid.uuid4().hex[:8]}"
        _register_and_login(driver, wait, "Black Box Vendor", "Vendor")

        driver.get(f"{base_url}/listings/new")
        wait.until(EC.visibility_of_element_located((By.NAME, "title")))
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        _fill_listing_form(
            driver,
            title,
            now + timedelta(days=2),
            now + timedelta(days=1),
        )
        driver.find_element(By.NAME, "submit").click()
        assert "Pickup window must end after it starts" in driver.find_element(
            By.TAG_NAME, "body"
        ).text
        driver.get(f"{base_url}/listings/mine")
        assert title not in driver.find_element(By.TAG_NAME, "body").text

        driver.get(f"{base_url}/listings/new")
        _fill_listing_form(
            driver,
            title,
            now - timedelta(hours=3),
            now - timedelta(hours=2),
        )
        driver.find_element(By.NAME, "submit").click()
        assert "Pickup window end cannot be in the past" in driver.find_element(
            By.TAG_NAME, "body"
        ).text
        driver.get(f"{base_url}/listings/mine")
        assert title not in driver.find_element(By.TAG_NAME, "body").text

        pickup_start = now + timedelta(days=1)
        pickup_end = now + timedelta(days=1, hours=1)
        driver.get(f"{base_url}/listings/new")
        _fill_listing_form(driver, title, pickup_start, pickup_end)
        driver.find_element(By.NAME, "submit").click()
        wait.until(EC.url_contains("/listings/mine"))
        vendor_listings = driver.find_element(By.TAG_NAME, "body").text
        assert title in vendor_listings
        assert "Black-box test listing" in vendor_listings
        assert "3 portions remaining" in vendor_listings
        assert "Student Union" in vendor_listings
        assert pickup_start.strftime("%a %b %d, %I:%M %p") in vendor_listings
        assert pickup_end.strftime("%a %b %d, %I:%M %p") in vendor_listings

        driver.get(f"{base_url}/auth/logout")
        driver.find_element(By.NAME, "submit").click()
        wait.until(EC.url_contains("/auth/login"))
        _register_and_login(driver, wait, "Black Box Student", "Student")

        driver.get(f"{base_url}/listings/")
        available_listings = driver.find_element(By.TAG_NAME, "body").text
        assert title in available_listings
        assert "Black Box Vendor" in available_listings
        assert "Student Union" in available_listings
        assert "vegan" in available_listings
        assert "3 portions available" in available_listings
        assert pickup_start.strftime("%a %b %d, %I:%M %p") in available_listings
        assert pickup_end.strftime("%a %b %d, %I:%M %p") in available_listings

        driver.get(f"{base_url}/listings/new")
        assert driver.title == "Access denied"
        assert "Only vendors can post listings." in driver.find_element(
            By.TAG_NAME, "body"
        ).text
    finally:
        driver.quit()
