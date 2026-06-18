from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import Tuple, List
from app.models.order import Order


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_paginated(self, page: int, page_size: int) -> Tuple[List[Order], int]:
        offset = (page - 1) * page_size
        total = self.db.execute(select(func.count()).select_from(Order)).scalar_one()
        orders = (
            self.db.execute(
                select(Order).offset(offset).limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(orders), total

    def bulk_insert(self, records: list[dict]) -> int:
        self.db.execute(Order.__table__.insert(), records)
        self.db.commit()
        return len(records)
