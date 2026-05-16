def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_item(client, sample_item):
    create_response = client.post("/api/items", json=sample_item)
    assert create_response.status_code == 201
    assert create_response.json()["name"] == "HDMI Cable"

    list_response = client.get("/api/items")
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1


def test_update_item_quantity(client, sample_item):
    item = client.post("/api/items", json=sample_item).json()
    response = client.put(f"/api/items/{item['id']}", json={"quantity": 3})
    assert response.status_code == 200
    assert response.json()["quantity"] == 3


def test_low_stock_filter(client, sample_item):
    item = client.post("/api/items", json=sample_item).json()
    client.put(f"/api/items/{item['id']}", json={"quantity": 2})

    response = client.get("/api/items?low_stock=true")
    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_delete_item(client, sample_item):
    item = client.post("/api/items", json=sample_item).json()
    response = client.delete(f"/api/items/{item['id']}")
    assert response.status_code == 204

    list_response = client.get("/api/items")
    assert list_response.json()["count"] == 0


def test_export_csv(client, sample_item):
    client.post("/api/items", json=sample_item)
    response = client.get("/api/items/export")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "HDMI Cable" in response.text

