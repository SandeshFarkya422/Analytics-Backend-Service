from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import Tuple, List
from app.models.refund import Refund


class RefundRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_paginated(self, page: int, page_size: int) -> Tuple[List[Refund], int]:
        offset = (page - 1) * page_size
        total = self.db.execute(select(func.count()).select_from(Refund)).scalar_one()
        refunds = (
            self.db.execute(
                select(Refund).offset(offset).limit(page_size)
            )
            .scalars()
            .all()
        )
        return list(refunds), total

    def bulk_insert(self, records: list[dict]) -> int:
        self.db.execute(Refund.__table__.insert(), records)
        self.db.commit()
        return len(records)
