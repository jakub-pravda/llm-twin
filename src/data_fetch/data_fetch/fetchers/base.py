from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import AsyncIterator, Optional

from data_fetch.keystore.base import BaseKeyStore
from data_fetch.models import FetchedData

from loguru import logger

class DataFetcherArg(Enum):
    DUMMY = "dummy"
    TELEGRAM = "telegram"


class BaseDataFetcher(ABC):
    FETCHER_NAME: str
    
    @abstractmethod
    def fetch(self, offset_date: datetime) -> AsyncIterator[FetchedData]:  # TODO type
        pass

    @staticmethod
    def get_fetcher_by_arg(
        data_fetcher_arg: DataFetcherArg, key_store: Optional[BaseKeyStore]
    ) -> Optional["BaseDataFetcher"]:
        logger.debug(f"Getting fetcher by arg: {data_fetcher_arg}")
        match data_fetcher_arg:
            case DataFetcherArg.DUMMY:
                from .dummy import DummyDataFetcher
                return DummyDataFetcher()
            case DataFetcherArg.TELEGRAM:
                from .telegram import TelegramDataFetcher

                if not key_store:
                    raise ValueError("Key store must be defined for Telegram fetcher")

                telegram_api_credentials = key_store.telegram_api_credentials()

                return TelegramDataFetcher(
                    telegram_credentials=telegram_api_credentials,
                    entity_ids=("+420 731 221 662",), # TODO entity ids to 
                )
            case _:
                return None
