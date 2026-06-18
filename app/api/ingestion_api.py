import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.ingestion_service import IngestionService
from app.schemas.analytics import IngestionResponse
from app.core.logging import logger

router = APIRouter(tags=["Ingestion"])


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_data(db: Session = Depends(get_db)):
    """
    Triggers full data ingestion from the mock API endpoints into MySQL.
    Pulls customers, orders, and refunds with automatic pagination.
    After ingestion, refreshes analytics summary tables.
    """
    try:
        logger.info("Starting full data ingestion...")
        service = IngestionService(db)
        result = await service.run()
        logger.info(f"Ingestion completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
