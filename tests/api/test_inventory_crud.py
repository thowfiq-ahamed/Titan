"""
API tests for Inventory Item CRUD endpoints.
"""

from fastapi.testclient import TestClient


def test_create_and_get_item(client: TestClient):
    payload = {
        "sku": "TITAN-RACK-01",
        "name": "Server Rack 42U",
        "description": "Standard 19-inch 42U rack cabinet",
        "category": "infrastructure",
        "quantity": 8,
        "price": 1150.00
    }
    # 1. Create Item
    post_res = client.post("/items", json=payload)
    assert post_res.status_code == 201
    created_data = post_res.json()
    assert created_data["sku"] == "TITAN-RACK-01"
    assert created_data["id"] is not None
    assert "X-Correlation-ID" in post_res.headers

    item_id = created_data["id"]

    # 2. Get Item by ID
    get_res = client.get(f"/items/{item_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Server Rack 42U"


def test_create_item_duplicate_sku_conflict(client: TestClient):
    payload = {
        "sku": "TITAN-DUP-01",
        "name": "Original Item",
        "category": "compute",
        "quantity": 2,
        "price": 500.00
    }
    res1 = client.post("/items", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/items", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_list_items_with_pagination_and_filter(client: TestClient):
    # Seed items
    client.post("/items", json={"sku": "TITAN-FLT-A", "name": "Storage SAN", "category": "storage", "quantity": 3, "price": 8000.0})
    client.post("/items", json={"sku": "TITAN-FLT-B", "name": "Compute Blade", "category": "compute", "quantity": 10, "price": 2000.0})

    # Query all
    res = client.get("/items?limit=10")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 2
    assert len(body["items"]) >= 2

    # Filter by category
    filter_res = client.get("/items?category=storage")
    assert filter_res.status_code == 200
    filter_body = filter_res.json()
    assert all(item["category"] == "storage" for item in filter_body["items"])


def test_update_item(client: TestClient):
    create_res = client.post("/items", json={"sku": "TITAN-UPD-01", "name": "Initial Name", "category": "compute", "quantity": 1, "price": 100.0})
    item_id = create_res.json()["id"]

    update_payload = {"name": "Updated Name", "quantity": 15, "price": 120.0}
    put_res = client.put(f"/items/{item_id}", json=update_payload)
    assert put_res.status_code == 200
    updated_data = put_res.json()
    assert updated_data["name"] == "Updated Name"
    assert updated_data["quantity"] == 15
    assert updated_data["price"] == 120.0


def test_delete_item(client: TestClient):
    create_res = client.post("/items", json={"sku": "TITAN-DEL-01", "name": "Item to Delete", "category": "general", "quantity": 1, "price": 50.0})
    item_id = create_res.json()["id"]

    # Delete
    del_res = client.delete(f"/items/{item_id}")
    assert del_res.status_code == 204

    # Verify 404
    get_res = client.get(f"/items/{item_id}")
    assert get_res.status_code == 404


def test_get_nonexistent_item_returns_404(client: TestClient):
    res = client.get("/items/non-existent-uuid-12345")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_validation_error_returns_rfc_details(client: TestClient):
    # Invalid payload (missing required SKU)
    res = client.post("/items", json={"name": "No SKU Item"})
    assert res.status_code == 422
    body = res.json()
    assert body["error"] == "ValidationError"
    assert "details" in body
