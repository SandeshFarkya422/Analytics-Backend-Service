from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import List


class OrderBase(BaseModel):
    customer_id: int
    amount: Decimal
    order_date: datetime


class OrderCreate(OrderBase):
    order_id: int


class OrderResponse(OrderBase):
    order_id: int

    model_config = {"from_attributes": True}


class PaginatedOrders(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int
    data: List[OrderResponse]
