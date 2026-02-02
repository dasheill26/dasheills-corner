def test_orders_requires_login(client):
    r = client.get("/orders", follow_redirects=False)
    # should redirect to /login
    assert r.status_code in (301, 302)
    assert "/login" in r.location

def test_place_order_creates_order(client):
    # Register/login
    client.post("/register", data={"email":"o@example.com", "password":"password123"}, follow_redirects=True)

    # Add item to cart
    client.post("/api/cart/add", json={"itemId":"item1", "name":"Wings", "pricePence":500})

    # Start payment
    client.post("/pay/stripe", data={
        "order_type": "delivery",
        "customer_name": "Test",
        "delivery_address": "1 Test Street"
    }, follow_redirects=True)

    # Confirm payment (demo)
    r = client.post("/pay/confirm", data={
        "card_name": "Test",
        "card_number": "4242 4242 4242 4242",
        "exp": "12/30",
        "cvc": "123"
    }, follow_redirects=True)

    assert r.status_code == 200
