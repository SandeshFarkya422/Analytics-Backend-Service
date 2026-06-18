import pytest
from decimal import Decimal
from datetime import datetime
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.refund_repository import RefundRepository
from app.repositories.analytics_repository import AnalyticsRepository


def test_customer_bulk_insert(db):
    repo = CustomerRepository(db)
    records = [
        {"customer_id": i, "name": f"User {i}", "email": f"u{i}@test.com",
         "created_at": datetime(2023, 1, 1)}
        for i in range(1, 11)
    ]
    count = repo.bulk_insert(records)
    assert count == 10


def test_customer_get_paginated(db, sample_customers):
    repo = CustomerRepository(db)
    customers, total = repo.get_paginated(1, 3)
    assert total == 5
    assert len(customers) == 3


def test_customer_get_paginated_page2(db, sample_customers):
    repo = CustomerRepository(db)
    customers, total = repo.get_paginated(2, 3)
    assert total == 5
    assert len(customers) == 2


def test_order_bulk_insert(db, sample_customers):
    repo = OrderRepository(db)
    records = [
        {"order_id": i, "customer_id": 1, "amount": Decimal("100.00"),
         "order_date": datetime(2023, 6, 1)}
        for i in range(1, 6)
    ]
    count = repo.bulk_insert(records)
    assert count == 5


def test_refund_bulk_insert(db, sample_orders):
    repo = RefundRepository(db)
    records = [
        {"refund_id": 1, "order_id": 1, "refund_amount": Decimal("50.00"),
         "refund_date": datetime(2023, 6, 10)}
    ]
    count = repo.bulk_insert(records)
    assert count == 1


def test_analytics_total_orders(db, sample_orders):
    repo = AnalyticsRepository(db)
    assert repo.get_total_orders() == 4


def test_analytics_total_revenue(db, sample_orders):
    repo = AnalyticsRepository(db)
    assert float(repo.get_total_revenue()) == pytest.approx(525.0)


def test_analytics_total_refunds(db, sample_refunds):
    repo = AnalyticsRepository(db)
    assert float(repo.get_total_refunds()) == pytest.approx(125.0)


def test_analytics_net_revenue(db, sample_orders, sample_refunds):
    repo = AnalyticsRepository(db)
    assert float(repo.get_net_revenue()) == pytest.approx(400.0)


def test_analytics_average_order_value(db, sample_orders):
    repo = AnalyticsRepository(db)
    assert float(repo.get_average_order_value()) == pytest.approx(131.25)


def test_analytics_top_customers(db, sample_orders):
    repo = AnalyticsRepository(db)
    top = repo.get_top_customers(limit=10)
    assert len(top) > 0
    assert top[0]["customer_id"] == 1


def test_analytics_revenue_trends(db, sample_orders):
    repo = AnalyticsRepository(db)
    trends = repo.get_revenue_trends()
    assert len(trends) > 0
    assert "month" in trends[0]
    assert "revenue" in trends[0]
