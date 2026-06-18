import json
from pathlib import Path
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.refund_repository import RefundRepository
from app.core.logging import logger

DATA_DIR = Path("data")


class MockDataService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.order_repo = OrderRepository(db)
        self.refund_repo = RefundRepository(db)

    def _paginate_json_file(
        self,
        filename: str,
        page: int,
        page_size: int,
    ) -> Dict[str, Any]:

        file_path = DATA_DIR / filename

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {
                "page": page,
                "page_size": page_size,
                "total_records": 0,
                "total_pages": 0,
                "data": [],
            }

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        total_records = len(data)

        start = (page - 1) * page_size
        end = start + page_size

        paginated_data = data[start:end]

        total_pages = (
            total_records + page_size - 1
        ) // page_size

        return {
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "total_pages": total_pages,
            "data": paginated_data,
        }

    def get_customers_paginated(
        self,
        page: int,
        page_size: int,
    ) -> Dict[str, Any]:

        return self._paginate_json_file(
            "customers.json",
            page,
            page_size,
        )

    def get_orders_paginated(
        self,
        page: int,
        page_size: int,
    ) -> Dict[str, Any]:

        return self._paginate_json_file(
            "orders.json",
            page,
            page_size,
        )

    def get_refunds_paginated(
        self,
        page: int,
        page_size: int,
    ) -> Dict[str, Any]:

        return self._paginate_json_file(
            "refunds.json",
            page,
            page_size,
        )

    def load_from_json(self) -> Dict[str, int]:
        """
        Direct JSON -> MySQL load
        (optional utility method)
        """

        result = {
            "customers_loaded": 0,
            "orders_loaded": 0,
            "refunds_loaded": 0,
        }

        batch_size = 5000

        customers_file = DATA_DIR / "customers.json"

        if customers_file.exists():
            logger.info("Loading customers from JSON...")

            with open(customers_file, "r", encoding="utf-8") as f:
                customers = json.load(f)

            for i in range(0, len(customers), batch_size):
                batch = customers[i:i + batch_size]
                self.customer_repo.bulk_insert(batch)

            result["customers_loaded"] = len(customers)

        orders_file = DATA_DIR / "orders.json"

        if orders_file.exists():
            logger.info("Loading orders from JSON...")

            with open(orders_file, "r", encoding="utf-8") as f:
                orders = json.load(f)

            for i in range(0, len(orders), batch_size):
                batch = orders[i:i + batch_size]
                self.order_repo.bulk_insert(batch)

            result["orders_loaded"] = len(orders)

        refunds_file = DATA_DIR / "refunds.json"

        if refunds_file.exists():
            logger.info("Loading refunds from JSON...")

            with open(refunds_file, "r", encoding="utf-8") as f:
                refunds = json.load(f)

            for i in range(0, len(refunds), batch_size):
                batch = refunds[i:i + batch_size]
                self.refund_repo.bulk_insert(batch)

            result["refunds_loaded"] = len(refunds)

        return result