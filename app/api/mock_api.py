from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.mock_data_service import MockDataService
from app.schemas.customer import PaginatedCustomers
from app.schemas.order import PaginatedOrders
from app.schemas.refund import PaginatedRefunds
from app.core.logging import logger

router = APIRouter(tags=["Mock Data"])


def validate_pagination(page: int, page_size: int) -> None:
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if page_size < 1 or page_size > 5000:
        raise HTTPException(status_code=400, detail="page_size must be between 1 and 5000")


@router.get("/customers", response_model=PaginatedCustomers)
def get_customers(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=1000, ge=1, le=5000, description="Records per page"),
    db: Session = Depends(get_db),
):
    validate_pagination(page, page_size)
    service = MockDataService(db)
    result = service.get_customers_paginated(page, page_size)
    return result


@router.get("/orders", response_model=PaginatedOrders)
def get_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=1000, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    validate_pagination(page, page_size)
    service = MockDataService(db)
    result = service.get_orders_paginated(page, page_size)
    return result


@router.get("/refunds", response_model=PaginatedRefunds)
def get_refunds(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=1000, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    validate_pagination(page, page_size)
    service = MockDataService(db)
    result = service.get_refunds_paginated(page, page_size)
    return result
