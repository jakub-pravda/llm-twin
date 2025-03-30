import random
from datetime import datetime
from typing import AsyncIterator

from data_fetch.fetchers.base import BaseDataFetcher, DataFetcherArg
from data_fetch.models import DummyFetchedData


class DummyDataFetcher(BaseDataFetcher):
    FETCHER_NAME = DataFetcherArg.DUMMY.value
    
    async def fetch(self, offset_date: datetime) -> AsyncIterator[DummyFetchedData]:
        yield DummyFetchedData(
            dummy_content=f"Dummy message {random.randint(1, 1000)}",
            source=DataFetcherArg.DUMMY.value,
            created_at=datetime.now(),
        )