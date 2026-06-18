from sqlalchemy import Column, Integer, Numeric, String, DateTime
from sqlalchemy.sql import func
from app.database.base import Base


class AnalyticsSummary(Base):
    """Aggregate summary table for fast analytics queries."""
    __tablename__ = "analytics_summary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(100), nullable=False, unique=True)
    metric_value = Column(Numeric(20, 4), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class RevenueByMonth(Base):
    """Pre-aggregated monthly revenue for trend analytics."""
    __tablename__ = "revenue_by_month"

    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(String(7), nullable=False, unique=True)
    revenue = Column(Numeric(20, 2), nullable=False)
    order_count = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
