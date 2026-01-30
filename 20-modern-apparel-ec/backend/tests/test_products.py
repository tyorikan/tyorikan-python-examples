import os

# Force emulator env
os.environ["SPANNER_EMULATOR_HOST"] = "localhost:9010"
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
os.environ["SPANNER_INSTANCE"] = "test-instance"
os.environ["SPANNER_DATABASE"] = "test-database"

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_create_and_list_products():
    # Create Product
    response = client.post("/api/products/", json={
        "name": "Airism T-Shirt",
        "description": "Cool and comfortable",
        "base_price": 1500,
        "category_id": "men-tops",
        "variants": [
            {"variant_id": "v1", "color": "White", "size": "L", "stock_quantity": 100},
            {"variant_id": "v2", "color": "Black", "size": "M", "stock_quantity": 50}
        ]
    })
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["status"] == "created"
    product_id = data["product_id"]

    # Get Product
    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    p_data = res_json["data"]
    assert p_data["name"] == "Airism T-Shirt"
    assert len(p_data["variants"]) == 2
    assert p_data["variants"][0]["color"] == "White"

    # List Products
    response = client.get("/api/products/")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    l_data = res_json["data"]
    assert len(l_data) >= 1
    # Check if our product is in list
    found = any(p["product_id"] == product_id for p in l_data)
    assert found

