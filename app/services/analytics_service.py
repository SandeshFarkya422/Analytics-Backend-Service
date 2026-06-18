from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Dict, Any
from app.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, db: Session):
        self.repo = AnalyticsRepository(db)

    def get_total_orders(self) -> int:
        return self.repo.get_total_orders()

    def get_total_revenue(self) -> Decimal:
        return self.repo.get_total_revenue()

    def get_total_refunds(self) -> Decimal:
        return self.repo.get_total_refunds()

    def get_net_revenue(self) -> Decimal:
        return self.repo.get_net_revenue()

    def get_average_order_value(self) -> Decimal:
        return self.repo.get_average_order_value()

    def get_repeat_customer_revenue(self) -> Decimal:
        return self.repo.get_repeat_customer_revenue()

    def get_revenue_trends(self) -> List[Dict[str, Any]]:
        return self.repo.get_revenue_trends()

    def get_top_customers(self) -> List[Dict[str, Any]]:
        return self.repo.get_top_customers(limit=10)
