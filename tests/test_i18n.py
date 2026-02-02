def test_language_switch_sets_session(client):
    r = client.get("/lang/es", follow_redirects=False)
    assert r.status_code in (301, 302)

    # after setting language, open menu (should still load)
    r2 = client.get("/menu")
    assert r2.status_code == 200
