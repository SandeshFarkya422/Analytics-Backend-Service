from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List


class CustomerBase(BaseModel):
    name: str
    email: str
    created_at: datetime


class CustomerCreate(CustomerBase):
    customer_id: int


class CustomerResponse(CustomerBase):
    customer_id: int

    model_config = {"from_attributes": True}


class PaginatedCustomers(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int
    data: List[CustomerResponse]
