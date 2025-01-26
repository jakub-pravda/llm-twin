from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import AsyncIterator, Optional

from data_fetch.keystore.base import BaseKeyStore
from data_fetch.models import FetchedData


class DataFetcherArg(Enum):
    TELEGRAM = "telegram"


class BaseDataFetcher(ABC):
    @abstractmethod
    def fetch(self, offset_date: datetime) -> AsyncIterator[FetchedData]:  # TODO type
        pass
    
    @staticmethod
    def get_fetcher_by_arg(
        data_fetcher_arg: DataFetcherArg, key_store: BaseKeyStore
    ) -> Optional['BaseDataFetcher']:
        match data_fetcher_arg:
            case DataFetcherArg.TELEGRAM:
                from .telegram import TelegramDataFetcher
                telegram_api_credentials = key_store.telegram_api_credentials()

                return TelegramDataFetcher(telegram_credentials=telegram_api_credentials, entity_ids=("+420 731 221 662",))
            case _:
                return None
