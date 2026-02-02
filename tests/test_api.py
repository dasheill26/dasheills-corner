def test_menu_api(client):
    r = client.get("/api/menu")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
