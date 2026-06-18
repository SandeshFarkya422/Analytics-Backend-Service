import pytest
from decimal import Decimal


def test_total_orders_empty(client):
    response = client.get("/analytics/total-orders")
    assert response.status_code == 200
    assert response.json()["total_orders"] == 0


def test_total_orders(client, sample_orders):
    response = client.get("/analytics/total-orders")
    assert response.status_code == 200
    assert response.json()["total_orders"] == 4


def test_total_revenue_empty(client):
    response = client.get("/analytics/total-revenue")
    assert response.status_code == 200
    assert float(response.json()["total_revenue"]) == 0.0


def test_total_revenue(client, sample_orders):
    # 100 + 200 + 150 + 75 = 525
    response = client.get("/analytics/total-revenue")
    assert response.status_code == 200
    assert float(response.json()["total_revenue"]) == pytest.approx(525.0)


def test_total_refunds(client, sample_refunds):
    # 50 + 75 = 125
    response = client.get("/analytics/total-refunds")
    assert response.status_code == 200
    assert float(response.json()["total_refunds"]) == pytest.approx(125.0)


def test_net_revenue(client, sample_orders, sample_refunds):
    # 525 - 125 = 400
    response = client.get("/analytics/net-revenue")
    assert response.status_code == 200
    assert float(response.json()["net_revenue"]) == pytest.approx(400.0)


def test_average_order_value(client, sample_orders):
    # 525 / 4 = 131.25
    response = client.get("/analytics/average-order-value")
    assert response.status_code == 200
    assert float(response.json()["average_order_value"]) == pytest.approx(131.25)


def test_average_order_value_empty(client):
    response = client.get("/analytics/average-order-value")
    assert response.status_code == 200
    assert float(response.json()["average_order_value"]) == 0.0


def test_repeat_customer_revenue(client, sample_orders):
    # customer_id=1 has 2 orders (100 + 200 = 300) — repeat customer
    response = client.get("/analytics/repeat-customer-revenue")
    assert response.status_code == 200
    assert float(response.json()["repeat_customer_revenue"]) == pytest.approx(300.0)


def test_revenue_trends(client, sample_orders):
    response = client.get("/analytics/revenue-trends")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    item = data[0]
    assert "month" in item
    assert "revenue" in item


def test_top_customers(client, sample_orders):
    response = client.get("/analytics/top-customers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # customer_id=1 should be top with 300
    assert data[0]["customer_id"] == 1
    assert float(data[0]["total_spend"]) == pytest.approx(300.0)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
