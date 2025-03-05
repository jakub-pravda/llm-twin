import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Iterable, List, Mapping, Optional, Tuple

from loguru import logger
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from data_fetch.models import FetchedData


class DocumentStorage(ABC):
    @abstractmethod
    async def insert(self, fetched_data: AsyncIterator[FetchedData]) -> None:
        pass


class MongoDocumentStorage(DocumentStorage):
    DEFAULT_BATCH_SIZE = 100

    def __init__(self, mongo_host: str, mongo_port: int, database_name: str):
        self.database_name = database_name
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port

    def get_last_inserted(self, collection: str) -> Optional[FetchedData]:
        db = self.__client()[self.database_name]
        source_collection = db[collection]
        last_inserted = source_collection.find_one(sort=[("created_at", -1)])
        if last_inserted is None:
            return None
        else:
            return FetchedData.model_validate(last_inserted)

    async def insert(self, fetched_data: AsyncIterator[FetchedData]) -> None:
        number_of_attempts = 3

        while True:
            logger.debug("Batch insertion started")
            has_next, data_batch = await self.__get_data_batch(
                iter=fetched_data, size=self.DEFAULT_BATCH_SIZE
            )

            self.__attempt_insert(data_batch, number_of_attempts)
            logger.debug("Batch insertion finished")

            if not has_next:
                logger.debug("Fetched data iterator exhausted")
                break

        logger.info("Fetched data insertion finished")

    def __attempt_insert(
        self, data_batch: Iterable[FetchedData], number_of_attempts: int
    ) -> None:
        src = "telegram"  # TODO
        db = self.__client()[self.database_name]
        data_batch_dumped = [item.model_dump(by_alias=True) for item in data_batch]

        if len(data_batch_dumped) == 0:
            logger.debug("No data to insert")
            return

        for attempt in range(1, 1 + number_of_attempts):
            try:
                logger.debug(
                    "Inserting batch to the doc store. Attempt number {}/{}",
                    attempt,
                    number_of_attempts,
                )
                source_collection = db[src]
                insert_many_result = source_collection.insert_many(data_batch_dumped)

                len_data_batch = len(data_batch_dumped)
                len_inserted = len(insert_many_result.inserted_ids)

                if len_data_batch == len_inserted:
                    # success
                    logger.debug(
                        "Successfully inserted batch with {} documents", len_inserted
                    )
                    break
                else:
                    logger.warning(
                        "Batch insertion failed. Inserted {len_insert} of {len_batch} records",
                        len_insert=len_inserted,
                        len_batch=len_data_batch,
                    )

                if attempt >= number_of_attempts:
                    # for now, just log the error
                    logger.error(
                        "Batch insertion failed after {} attempts", number_of_attempts
                    )

            except ServerSelectionTimeoutError as e:
                logger.error("Connection failed. Err {}", e)
                if attempt >= number_of_attempts:
                    raise e
            except Exception as e:
                logger.error("Document insertion failed with exception. Error {}", e)
                # unknown error, skip other attempts
                raise e

    def __client(self) -> MongoClient[Mapping[str, Any]]:
        username = urllib.parse.quote_plus("root")  # TODO store secrets
        password = urllib.parse.quote_plus("example")  # TODO store secrets

        mongo_client = MongoClient(
            f"mongodb://{username}:{password}@{self.mongo_host}:{self.mongo_port}"
        )  # type:ignore
        logger.debug("Mongo client object id: {}", id(mongo_client))  # TODO delete
        return mongo_client

    async def __get_data_batch(
        self, iter: AsyncIterator[FetchedData], size: int
    ) -> Tuple[bool, Iterable[FetchedData]]:
        sentinel = object()
        data_batch: List[FetchedData] = []
        for _ in range(size):
            iter_next = await anext(iter, sentinel)
            if iter_next == sentinel:
                return (False, data_batch)
            else:
                # remark: ignore type check due to sentinel object
                data_batch.append(iter_next)  # type:ignore
        return (True, data_batch)
