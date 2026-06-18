from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import List


class RefundBase(BaseModel):
    order_id: int
    refund_amount: Decimal
    refund_date: datetime


class RefundCreate(RefundBase):
    refund_id: int


class RefundResponse(RefundBase):
    refund_id: int

    model_config = {"from_attributes": True}


class PaginatedRefunds(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int
    data: List[RefundResponse]
