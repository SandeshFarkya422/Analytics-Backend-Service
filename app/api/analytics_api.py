from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    TotalOrdersResponse,
    TotalRevenueResponse,
    TotalRefundsResponse,
    NetRevenueResponse,
    AverageOrderValueResponse,
    RepeatCustomerRevenueResponse,
    RevenueTrendItem,
    TopCustomerItem,
)
from app.core.logging import logger

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


@router.get("/total-orders", response_model=TotalOrdersResponse)
def total_orders(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return {"total_orders": service.get_total_orders()}
    except Exception as e:
        logger.error(f"Error in total-orders: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/total-revenue", response_model=TotalRevenueResponse)
def total_revenue(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return {"total_revenue": service.get_total_revenue()}
    except Exception as e:
        logger.error(f"Error in total-revenue: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/total-refunds", response_model=TotalRefundsResponse)
def total_refunds(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return {"total_refunds": service.get_total_refunds()}
    except Exception as e:
        logger.error(f"Error in total-refunds: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/net-revenue", response_model=NetRevenueResponse)
def net_revenue(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return {"net_revenue": service.get_net_revenue()}
    except Exception as e:
        logger.error(f"Error in net-revenue: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/average-order-value", response_model=AverageOrderValueResponse)
def average_order_value(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return {"average_order_value": service.get_average_order_value()}
    except Exception as e:
        logger.error(f"Error in average-order-value: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repeat-customer-revenue", response_model=RepeatCustomerRevenueResponse)
def repeat_customer_revenue(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return {"repeat_customer_revenue": service.get_repeat_customer_revenue()}
    except Exception as e:
        logger.error(f"Error in repeat-customer-revenue: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue-trends", response_model=List[RevenueTrendItem])
def revenue_trends(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return service.get_revenue_trends()
    except Exception as e:
        logger.error(f"Error in revenue-trends: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-customers", response_model=List[TopCustomerItem])
def top_customers(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return service.get_top_customers()
    except Exception as e:
        logger.error(f"Error in top-customers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
