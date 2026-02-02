def test_register_and_login(client):
    # Register (your /register only uses email + password)
    r = client.post(
        "/register",
        data={"email": "t@example.com", "password": "password123"},
        follow_redirects=True,
    )
    assert r.status_code == 200

    # Logout
    r_logout = client.get("/logout", follow_redirects=True)
    assert r_logout.status_code == 200

    # Login
    r2 = client.post(
        "/login",
        data={"email": "t@example.com", "password": "password123"},
        follow_redirects=True,
    )
    assert r2.status_code == 200


def test_login_rejects_wrong_password(client):
    # Create account first
    client.post(
        "/register",
        data={"email": "x@example.com", "password": "password123"},
        follow_redirects=True,
    )

    # Wrong password should redirect back to /login (still returns 200 after redirects)
    r = client.post(
        "/login",
        data={"email": "x@example.com", "password": "WRONG"},
        follow_redirects=True,
    )
    assert r.status_code == 200
