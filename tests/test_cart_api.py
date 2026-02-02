def test_cart_add_and_setqty(client):
    r = client.post("/api/cart/add", json={"itemId":"item1", "name":"Wings", "pricePence":799})
    assert r.status_code == 200
    data = r.get_json()
    assert data["cartCount"] == 1

    r2 = client.post("/api/cart/setqty", json={"itemId":"item1", "qty":3})
    assert r2.status_code == 200
    data2 = r2.get_json()
    assert data2["cartCount"] == 3
    assert data2["subtotalPence"] == 799 * 3
