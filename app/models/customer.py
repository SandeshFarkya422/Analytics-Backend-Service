from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from app.database.base import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)

    orders = relationship("Order", back_populates="customer", lazy="dynamic")

    __table_args__ = (
        Index("idx_customers_email", "email"),
        Index("idx_customers_created_at", "created_at"),
    )
