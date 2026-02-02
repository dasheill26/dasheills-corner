from models import User, db

def test_rewards_points_increase_after_order(client):
    client.post("/register", data={"email":"p@example.com", "password":"password123"}, follow_redirects=True)

    # Add £10.00 to cart
    client.post("/api/cart/add", json={"itemId":"item1", "name":"Wings", "pricePence":1000})

    client.post("/pay/stripe", data={
        "order_type": "delivery",
        "customer_name": "Test",
        "delivery_address": "1 Test Street"
    }, follow_redirects=True)

    client.post("/pay/confirm", data={
        "card_name": "Test",
        "card_number": "4242 4242 4242 4242",
        "exp": "12/30",
        "cvc": "123"
    }, follow_redirects=True)

    # Check points in DB (5% of 1000p = 50 points)
    with client.application.app_context():
        u = User.query.filter_by(email="p@example.com").first()
        assert u.reward_points >= 50
