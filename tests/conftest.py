import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database.base import Base
from app.database.session import get_db
from app.models import Customer, Order, Refund  # noqa: F401
from datetime import datetime
from decimal import Decimal

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_customers(db):
    customers = [
        Customer(customer_id=i, name=f"User {i}", email=f"user{i}@test.com",
                 created_at=datetime(2023, 1, 1))
        for i in range(1, 6)
    ]
    db.add_all(customers)
    db.commit()
    return customers


@pytest.fixture
def sample_orders(db, sample_customers):
    orders = [
        Order(order_id=1, customer_id=1, amount=Decimal("100.00"), order_date=datetime(2023, 6, 1)),
        Order(order_id=2, customer_id=1, amount=Decimal("200.00"), order_date=datetime(2023, 7, 1)),
        Order(order_id=3, customer_id=2, amount=Decimal("150.00"), order_date=datetime(2023, 8, 1)),
        Order(order_id=4, customer_id=3, amount=Decimal("75.00"), order_date=datetime(2023, 9, 1)),
    ]
    db.add_all(orders)
    db.commit()
    return orders


@pytest.fixture
def sample_refunds(db, sample_orders):
    refunds = [
        Refund(refund_id=1, order_id=1, refund_amount=Decimal("50.00"), refund_date=datetime(2023, 6, 10)),
        Refund(refund_id=2, order_id=3, refund_amount=Decimal("75.00"), refund_date=datetime(2023, 8, 15)),
    ]
    db.add_all(refunds)
    db.commit()
    return refunds
