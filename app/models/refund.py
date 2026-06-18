from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.base import Base


class Refund(Base):
    __tablename__ = "refunds"

    refund_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    refund_amount = Column(Numeric(12, 2), nullable=False)
    refund_date = Column(DateTime, nullable=False)

    order = relationship("Order", back_populates="refunds")

    __table_args__ = (
        Index("idx_refunds_order_id", "order_id"),
        Index("idx_refunds_refund_date", "refund_date"),
    )
