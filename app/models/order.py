from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.base import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    order_date = Column(DateTime, nullable=False)

    customer = relationship("Customer", back_populates="orders")
    refunds = relationship("Refund", back_populates="order", lazy="dynamic")

    __table_args__ = (
        Index("idx_orders_customer_id", "customer_id"),
        Index("idx_orders_order_date", "order_date"),
        Index("idx_orders_customer_date", "customer_id", "order_date"),
    )
