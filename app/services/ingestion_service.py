import httpx
import asyncio
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import get_settings
from app.core.logging import logger
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.refund_repository import RefundRepository
from app.repositories.analytics_repository import AnalyticsRepository

settings = get_settings()


class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.base_url = settings.MOCK_API_BASE_URL
        self.batch_size = settings.INGESTION_BATCH_SIZE
        self.page_size = settings.INGESTION_PAGE_SIZE
        self.customer_repo = CustomerRepository(db)
        self.order_repo = OrderRepository(db)
        self.refund_repo = RefundRepository(db)
        self.analytics_repo = AnalyticsRepository(db)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _fetch_page(self, client: httpx.AsyncClient, endpoint: str, page: int) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        params = {"page": page, "page_size": self.page_size}
        response = await client.get(url, params=params, timeout=60.0)
        response.raise_for_status()
        return response.json()

    async def _ingest_entity(
        self,
        client: httpx.AsyncClient,
        endpoint: str,
        repo,
        entity_name: str,
    ) -> int:
        logger.info(f"Starting ingestion of {entity_name}...")
        first_page = await self._fetch_page(client, endpoint, 1)
        total_pages = first_page["total_pages"]
        total_records = first_page["total_records"]
        logger.info(f"{entity_name}: {total_records} records across {total_pages} pages")

        buffer: List[Dict] = []
        total_inserted = 0

        def flush_buffer(buf: List[Dict]) -> int:
            if not buf:
                return 0
            repo.bulk_insert(buf)
            return len(buf)

        # Process first page data
        buffer.extend(first_page["data"])
        if len(buffer) >= self.batch_size:
            total_inserted += flush_buffer(buffer)
            buffer = []

        # Fetch remaining pages concurrently in chunks of 10
        concurrency = 10
        for chunk_start in range(2, total_pages + 1, concurrency):
            chunk_end = min(chunk_start + concurrency, total_pages + 1)
            tasks = [
                self._fetch_page(client, endpoint, p)
                for p in range(chunk_start, chunk_end)
            ]
            pages = await asyncio.gather(*tasks, return_exceptions=True)
            for page_data in pages:
                if isinstance(page_data, Exception):
                    logger.error(f"Failed to fetch page: {page_data}")
                    continue
                buffer.extend(page_data["data"])
                if len(buffer) >= self.batch_size:
                    total_inserted += flush_buffer(buffer)
                    buffer = []
                    logger.info(f"{entity_name}: {total_inserted} records inserted so far")

        # Flush remaining
        total_inserted += flush_buffer(buffer)
        logger.info(f"{entity_name} ingestion complete: {total_inserted} records")
        return total_inserted

    async def run(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            customers_loaded = await self._ingest_entity(client, "customers", self.customer_repo, "customers")
            orders_loaded = await self._ingest_entity(client, "orders", self.order_repo, "orders")
            refunds_loaded = await self._ingest_entity(client, "refunds", self.refund_repo, "refunds")

        logger.info("Refreshing analytics summary tables...")
        self.analytics_repo.refresh_summary_metrics()
        logger.info("Analytics summary refresh complete.")

        return {
            "status": "completed",
            "customers_loaded": customers_loaded,
            "orders_loaded": orders_loaded,
            "refunds_loaded": refunds_loaded,
        }
