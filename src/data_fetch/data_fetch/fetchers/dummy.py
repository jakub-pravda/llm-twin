from datetime import datetime, timedelta
from typing import AsyncIterator, Tuple

from loguru import logger

from data_fetch.fetchers.base import BaseDataFetcher
from data_fetch.models import FetchedData

class DummyDataFetcher(BaseDataFetcher):
    FETCHER_NAME = "dummy"
    
    async def fetch(self, offset_date: datetime) -> AsyncIterator[FetchedData]:
        yield FetchedData(
            author="dummy fetcher",
            content="Dummy message",
            source="Dummy",
            created_at=datetime.now(),
        )