from sqlalchemy.orm import Session
from sqlalchemy import text, func, select
from decimal import Decimal
from typing import List, Dict, Any
from app.models.order import Order
from app.models.refund import Refund
from app.models.analytics_summary import AnalyticsSummary, RevenueByMonth


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_summary_metric(self, metric_name: str) -> Decimal | None:
        row = self.db.execute(
            select(AnalyticsSummary.metric_value).where(
                AnalyticsSummary.metric_name == metric_name
            )
        ).scalar_one_or_none()
        return row

    def get_total_orders(self) -> int:
        cached = self.get_summary_metric("total_orders")
        if cached is not None:
            return int(cached)
        result = self.db.execute(select(func.count()).select_from(Order)).scalar_one()
        return result

    def get_total_revenue(self) -> Decimal:
        cached = self.get_summary_metric("total_revenue")
        if cached is not None:
            return cached
        result = self.db.execute(select(func.sum(Order.amount))).scalar_one() or Decimal("0")
        return result

    def get_total_refunds(self) -> Decimal:
        cached = self.get_summary_metric("total_refunds")
        if cached is not None:
            return cached
        result = self.db.execute(select(func.sum(Refund.refund_amount))).scalar_one() or Decimal("0")
        return result

    def get_net_revenue(self) -> Decimal:
        total_revenue = self.get_total_revenue()
        total_refunds = self.get_total_refunds()
        return Decimal(str(total_revenue)) - Decimal(str(total_refunds))

    def get_average_order_value(self) -> Decimal:
        total_revenue = self.get_total_revenue()
        total_orders = self.get_total_orders()
        if total_orders == 0:
            return Decimal("0")
        return Decimal(str(total_revenue)) / Decimal(str(total_orders))

    def get_repeat_customer_revenue(self) -> Decimal:
        cached = self.get_summary_metric("repeat_customer_revenue")
        if cached is not None:
            return cached
        sql = text("""
            SELECT COALESCE(SUM(o.amount), 0)
            FROM orders o
            WHERE o.customer_id IN (
                SELECT customer_id
                FROM orders
                GROUP BY customer_id
                HAVING COUNT(*) > 1
            )
        """)
        result = self.db.execute(sql).scalar_one() or Decimal("0")
        return result

    def get_revenue_trends(self) -> List[Dict[str, Any]]:
        rows = self.db.execute(
            select(RevenueByMonth.month, RevenueByMonth.revenue)
            .order_by(RevenueByMonth.month)
        ).all()
        if rows:
            return [{"month": r.month, "revenue": r.revenue} for r in rows]
        # Fallback: compute directly — dialect-aware date truncation
        dialect = self._get_dialect()
        if dialect == "sqlite":
            sql = text("""
                SELECT strftime('%Y-%m', order_date) AS month,
                       SUM(amount) AS revenue
                FROM orders
                GROUP BY month
                ORDER BY month
            """)
        else:
            sql = text("""
                SELECT DATE_FORMAT(order_date, '%Y-%m') AS month,
                       SUM(amount) AS revenue
                FROM orders
                GROUP BY month
                ORDER BY month
            """)
        rows = self.db.execute(sql).all()
        return [{"month": r.month, "revenue": r.revenue} for r in rows]

    # def get_top_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
    #     sql = text("""
    #         SELECT customer_id, SUM(amount) AS total_spend
    #         FROM orders
    #         GROUP BY customer_id
    #         ORDER BY total_spend DESC
    #         LIMIT :limit
    #     """)
    #     rows = self.db.execute(sql, {"limit": limit}).all()
    #     return [{"customer_id": r.customer_id, "total_spend": r.total_spend} for r in rows]
    
    
    def get_top_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        sql = text("""
            SELECT customer_id, total_spend
            FROM  customer_spend
            ORDER BY total_spend DESC
            LIMIT :limit
        """)
        rows = self.db.execute(sql, {"limit": limit}).all()
        return [{"customer_id": r.customer_id, 
                 "total_spend": float(r.total_spend)
                 }
                for r in rows
                ]

    def _get_dialect(self) -> str:
        try:
            return self.db.get_bind().dialect.name
        except Exception:
            return "mysql"

    def refresh_summary_metrics(self) -> None:
        """Rebuild the analytics_summary table from raw data."""
        metrics = {}

        total_orders = self.db.execute(
            select(func.count()).select_from(Order)
        ).scalar_one()
        metrics["total_orders"] = total_orders

        total_revenue = self.db.execute(
            select(func.sum(Order.amount))
        ).scalar_one() or Decimal("0")
        metrics["total_revenue"] = total_revenue

        total_refunds = self.db.execute(
            select(func.sum(Refund.refund_amount))
        ).scalar_one() or Decimal("0")
        metrics["total_refunds"] = total_refunds

        rcr = self.db.execute(text("""
            SELECT COALESCE(SUM(o.amount), 0)
            FROM orders o
            WHERE o.customer_id IN (
                SELECT customer_id FROM orders GROUP BY customer_id HAVING COUNT(*) > 1
            )
        """)).scalar_one() or Decimal("0")
        metrics["repeat_customer_revenue"] = rcr

        for name, value in metrics.items():
            existing = self.db.execute(
                select(AnalyticsSummary).where(AnalyticsSummary.metric_name == name)
            ).scalar_one_or_none()
            if existing:
                existing.metric_value = value
            else:
                self.db.add(AnalyticsSummary(metric_name=name, metric_value=value))

        # Refresh revenue_by_month — dialect-aware
        self.db.execute(text("DELETE FROM revenue_by_month"))
        dialect = self._get_dialect()
        if dialect == "sqlite":
            monthly_sql = text("""
                SELECT strftime('%Y-%m', order_date) AS month,
                       SUM(amount) AS revenue,
                       COUNT(*) AS order_count
                FROM orders GROUP BY month
            """)
        else:
            monthly_sql = text("""
                SELECT DATE_FORMAT(order_date, '%Y-%m') AS month,
                       SUM(amount) AS revenue,
                       COUNT(*) AS order_count
                FROM orders GROUP BY month
            """)
        monthly = self.db.execute(monthly_sql).all()
        for row in monthly:
            self.db.add(RevenueByMonth(
                month=row.month,
                revenue=row.revenue,
                order_count=row.order_count,
            ))

        self.db.commit()
