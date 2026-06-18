from pydantic import BaseModel
from decimal import Decimal
from typing import List


class TotalOrdersResponse(BaseModel):
    total_orders: int


class TotalRevenueResponse(BaseModel):
    total_revenue: Decimal


class TotalRefundsResponse(BaseModel):
    total_refunds: Decimal


class NetRevenueResponse(BaseModel):
    net_revenue: Decimal


class AverageOrderValueResponse(BaseModel):
    average_order_value: Decimal


class RepeatCustomerRevenueResponse(BaseModel):
    repeat_customer_revenue: Decimal


class RevenueTrendItem(BaseModel):
    month: str
    revenue: Decimal


class TopCustomerItem(BaseModel):
    customer_id: int
    total_spend: Decimal


class IngestionResponse(BaseModel):
    status: str
    customers_loaded: int
    orders_loaded: int
    refunds_loaded: int
