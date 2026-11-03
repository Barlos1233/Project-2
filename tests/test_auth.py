def test_registration_login_home_and_logout(client):
    registration = client.post(
        "/register",
        data={
            "name": "New Student",
            "email": "new.student@example.com",
            "password": "password123",
            "role": "Student",
        },
    )
    assert registration.status_code == 302
    assert registration.headers["Location"].endswith("/auth/login")

    login_response = client.post(
        "/login",
        data={"email": "NEW.STUDENT@example.com", "password": "password123"},
    )
    assert login_response.status_code == 302
    assert login_response.headers["Location"].endswith("/student/home")

    home = client.get("/student/home")
    assert home.status_code == 200
    assert b"New Student" in home.data

    logout_response = client.post("/logout")
    assert logout_response.status_code == 302
    assert logout_response.headers["Location"].endswith("/auth/login")

    assert client.get("/student/home").status_code == 302
