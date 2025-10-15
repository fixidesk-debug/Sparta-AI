def test_health_endpoint(client):
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json().get('status') in ('ok', 'healthy')
