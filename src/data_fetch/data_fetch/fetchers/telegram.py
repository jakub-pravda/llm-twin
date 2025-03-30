from datetime import datetime, timedelta
from typing import AsyncIterator, Tuple

from loguru import logger
from telethon import TelegramClient  # type: ignore

from data_fetch.fetchers.base import BaseDataFetcher, DataFetcherArg
from data_fetch.models import TelegramApiCredentials, TelegramFetchedData


class TelegramDataFetcher(BaseDataFetcher):
    
    DEFAULT_MESSAGE_OFFSET = datetime.now() - timedelta(days=365)  # 1 year
    FETCHER_NAME = DataFetcherArg.TELEGRAM.value

    def __init__(
        self, telegram_credentials: TelegramApiCredentials, entity_ids: Tuple[str, ...]
    ):
        self.client = TelegramClient(
            "telegram_data_fetcher",
            telegram_credentials.api_id,
            telegram_credentials.api_hash,
        )
        self.entity_ids = entity_ids

    async def fetch(self, offset_date: datetime) -> AsyncIterator[TelegramFetchedData]:
        await self.__init__client()

        for entity_id in self.entity_ids:
            logger.info(f"Fetching messages for entity ID: {entity_id}")
            async for message in self.fetch_by_entity_id(entity_id, offset_date):
                yield message

    # TODO pydantic data types
    async def fetch_by_entity_id(
        self, entity_id: str, offset_date: datetime
    ) -> AsyncIterator[TelegramFetchedData]:
        message_iterator = self.client.iter_messages(
            entity_id, reverse=True, offset_date=offset_date
        )
        async for message in message_iterator:
            logger.debug(f"Raw Telethon fetched message: {message}")
            if message.message:
                # return only messages with text content
                sender_id = str(message.sender_id)
                yield TelegramFetchedData(
                    author=sender_id,
                    content=message.message,
                    source=DataFetcherArg.TELEGRAM.value,
                    created_at=message.date,
                )

    async def __init__client(self) -> None:
        try:
            logger.debug("Checking if Telegram client is connected")
            connected = self.client.is_connected()
            if connected:
                logger.debug("Telegram client already connected")
                return
            else:
                logger.info("Starting and connecting Telegram client")
                await self.client.start()
                await self.client.connect()
        except OSError as e:
            logger.error(f"Error connecting to Telegram client: {e}")
            raise e

    def __get_offset_date(self) -> datetime:
        # TODO compute last message offset?
        return self.DEFAULT_MESSAGE_OFFSET
