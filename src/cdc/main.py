import urllib.parse
from typing import Any, Mapping

from loguru import logger
from pymongo import MongoClient


# TODO mongo db client to share?
class MongoCDC:
    def __init__(self, mongo_host: str, mongo_port: int, database_name: str):
        self.database_name = database_name
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port

    def watch(self) -> None:
        db = self.__client()[self.database_name]

        # watch for database inserts
        changes = db.watch([{"$match": {"operationType": {"$in": ["insert"]}}}])

        for change in changes:
            logger.debug("Change: {}", change)

    def __client(self) -> MongoClient[Mapping[str, Any]]:
        username = urllib.parse.quote_plus("root")  # TODO store secrets
        password = urllib.parse.quote_plus("example")  # TODO store secrets

        mongo_client = MongoClient(
            f"mongodb://{username}:{password}@{self.mongo_host}:{self.mongo_port}"
        )  # type:ignore
        logger.debug("Mongo client object id: {}", id(mongo_client))  # TODO delete
        return mongo_client


def main():
    pass
