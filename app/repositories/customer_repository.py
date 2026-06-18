from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import Tuple, List
from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_paginated(self, page: int, page_size: int) -> Tuple[List[Customer], int]:
        offset = (page - 1) * page_size
        total = self.db.execute(select(func.count()).select_from(Customer)).scalar_one()
        customers = (
            self.db.execute(
                select(Customer).offset(offset).limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(customers), total

    def bulk_insert(self, records: list[dict]) -> int:
        self.db.execute(Customer.__table__.insert(), records)
        self.db.commit()
        return len(records)
