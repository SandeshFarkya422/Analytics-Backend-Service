"""
Data generation script.
Generates 100,000 customers, 1,000,000 orders, 200,000 refunds.
Uses seed=42 for reproducibility.
Saves output to data/ directory as JSON.
"""
import json
import random
import os
from pathlib import Path
from datetime import datetime, timedelta
from faker import Faker

SEED = 42
NUM_CUSTOMERS = 100_000
NUM_ORDERS = 1_000_000
NUM_REFUNDS = 200_000

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

fake = Faker()
Faker.seed(SEED)
random.seed(SEED)


def random_datetime(start: datetime, end: datetime) -> datetime:
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def generate_customers() -> list[dict]:
    print(f"Generating {NUM_CUSTOMERS:,} customers...")
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    customers = []
    seen_emails: set[str] = set()
    i = 1
    while len(customers) < NUM_CUSTOMERS:
        email = fake.email()
        if email in seen_emails:
            email = f"user_{i}_{fake.email()}"
        seen_emails.add(email)
        customers.append({
            "customer_id": i,
            "name": fake.name(),
            "email": email,
            "created_at": random_datetime(start_date, end_date).isoformat(),
        })
        i += 1
        if i % 10000 == 0:
            print(f"  {i:,} customers generated...")
    print(f"  Done: {len(customers):,} customers")
    return customers


def generate_orders(customer_ids: list[int]) -> list[dict]:
    print(f"Generating {NUM_ORDERS:,} orders...")
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2024, 12, 31)
    orders = []
    for i in range(1, NUM_ORDERS + 1):
        orders.append({
            "order_id": i,
            "customer_id": random.choice(customer_ids),
            "amount": round(random.uniform(5.0, 2000.0), 2),
            "order_date": random_datetime(start_date, end_date).isoformat(),
        })
        if i % 100000 == 0:
            print(f"  {i:,} orders generated...")
    print(f"  Done: {len(orders):,} orders")
    return orders


def generate_refunds(order_ids: list[int], orders_map: dict[int, dict]) -> list[dict]:
    print(f"Generating {NUM_REFUNDS:,} refunds...")
    # Sample a subset of orders for refunds
    sampled_order_ids = random.sample(order_ids, NUM_REFUNDS)
    refunds = []
    for i, order_id in enumerate(sampled_order_ids, start=1):
        order = orders_map[order_id]
        order_date = datetime.fromisoformat(order["order_date"])
        refund_date = order_date + timedelta(days=random.randint(1, 30))
        refund_amount = round(random.uniform(1.0, float(order["amount"])), 2)
        refunds.append({
            "refund_id": i,
            "order_id": order_id,
            "refund_amount": refund_amount,
            "refund_date": refund_date.isoformat(),
        })
        if i % 50000 == 0:
            print(f"  {i:,} refunds generated...")
    print(f"  Done: {len(refunds):,} refunds")
    return refunds


def save_json(data: list[dict], filepath: Path, chunk_size: int = 100_000) -> None:
    print(f"Saving {filepath.name} ({len(data):,} records)...")
    with open(filepath, "w") as f:
        json.dump(data, f)
    size_mb = filepath.stat().st_size / (1024 * 1024)
    print(f"  Saved {filepath.name} ({size_mb:.1f} MB)")


def main():
    print("=" * 50)
    print("Data Generation Script (seed=42)")
    print("=" * 50)

    customers = generate_customers()
    save_json(customers, DATA_DIR / "customers.json")

    customer_ids = [c["customer_id"] for c in customers]
    orders = generate_orders(customer_ids)
    save_json(orders, DATA_DIR / "orders.json")

    orders_map = {o["order_id"]: o for o in orders}
    order_ids = list(orders_map.keys())
    refunds = generate_refunds(order_ids, orders_map)
    save_json(refunds, DATA_DIR / "refunds.json")

    print("\n" + "=" * 50)
    print("Generation complete!")
    print(f"  Customers : {len(customers):,}")
    print(f"  Orders    : {len(orders):,}")
    print(f"  Refunds   : {len(refunds):,}")
    print(f"  Files saved to: {DATA_DIR.resolve()}")
    print("=" * 50)


if __name__ == "__main__":
    main()
