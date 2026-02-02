def test_checkout_requires_login(client):
    r = client.get("/checkout", follow_redirects=False)
    assert r.status_code in (301, 302)
    assert "/login" in r.location

def test_cannot_register_duplicate_email(client):
    client.post("/register", data={"email":"dup@example.com", "password":"password123"}, follow_redirects=True)
    r = client.post("/register", data={"email":"dup@example.com", "password":"password123"}, follow_redirects=False)
    # should redirect away (to login) because already registered
    assert r.status_code in (301, 302)
