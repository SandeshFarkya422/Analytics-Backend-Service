import pytest
from decimal import Decimal


def test_get_customers_empty(client):
    response = client.get("/customers?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_records"] == 0
    assert data["total_pages"] == 0
    assert data["data"] == []


def test_get_customers_with_data(client, sample_customers):
    response = client.get("/customers?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 5
    assert len(data["data"]) == 5
    assert data["total_pages"] == 1


def test_get_customers_pagination(client, sample_customers):
    response = client.get("/customers?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 5
    assert data["total_pages"] == 3
    assert len(data["data"]) == 2

    response_p2 = client.get("/customers?page=2&page_size=2")
    assert response_p2.status_code == 200
    data_p2 = response_p2.json()
    assert len(data_p2["data"]) == 2


def test_get_customers_invalid_page(client):
    response = client.get("/customers?page=0&page_size=10")
    assert response.status_code == 422


def test_get_customers_invalid_page_size(client):
    response = client.get("/customers?page=1&page_size=10000")
    assert response.status_code == 422


def test_get_orders_empty(client):
    response = client.get("/orders?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 0


def test_get_orders_with_data(client, sample_orders):
    response = client.get("/orders?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 4
    assert len(data["data"]) == 4


def test_get_refunds_with_data(client, sample_refunds):
    response = client.get("/refunds?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 2


def test_customer_fields(client, sample_customers):
    response = client.get("/customers?page=1&page_size=5")
    assert response.status_code == 200
    customer = response.json()["data"][0]
    assert "customer_id" in customer
    assert "name" in customer
    assert "email" in customer
    assert "created_at" in customer


def test_order_fields(client, sample_orders):
    response = client.get("/orders?page=1&page_size=10")
    assert response.status_code == 200
    order = response.json()["data"][0]
    assert "order_id" in order
    assert "customer_id" in order
    assert "amount" in order
    assert "order_date" in order
