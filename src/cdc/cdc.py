from typing import Any, Mapping, Optional

import click
from kombu import Connection, Exchange, Queue  # type: ignore
from loguru import logger
from pymongo import MongoClient
from pymongo.change_stream import ChangeStream


class AqmpPublisher:
    def __init__(self, rabbit_mq_host: str):
        self.__aqmp_connection_string = f"amqp://{rabbit_mq_host}//"

        # TODO move it to share
        self.__feature_pipeline_exchange = Exchange(
            "feature_pipeline", type="direct"
        )
        self.__feature_pipeline_routing_key = "feature_pipeline"
        self.__feature_pipeline_queue = Queue(
            "feature_pipeline",
            exchange=self.__feature_pipeline_exchange,
            routing_key=self.__feature_pipeline_routing_key,
        )

    def publish(self, document: Mapping[str, Any]) -> None:
        logger.debug("Aqmp publisher, sending document {}", document)
        with Connection(self.__aqmp_connection_string) as conn:
            producer = conn.Producer(serializer="json")
            producer.publish(
                document,
                exchange=self.__feature_pipeline_exchange,
                routing_key=self.__feature_pipeline_routing_key,
                declare=[self.__feature_pipeline_queue],
            )
            logger.debug(
                "Aqmp publisher, document has been published {}", document
            )


class MongoCDC:
    def __init__(self, mongo_host: str, mongo_port: int, database_name: str):
        self.database_name = database_name
        self.mongo_host = mongo_host
        self.mongo_port = mongo_port

    def __client(self) -> MongoClient[Mapping[str, Any]]:
        mongo_conn_string = f"mongodb://{self.mongo_host}:{self.mongo_port}"
        logger.info(
            f"Connecting to mongo with connection string {mongo_conn_string}"
        )

        mongo_client = MongoClient(mongo_conn_string)  # type:ignore
        logger.debug(
            "Mongo client object id: {}", id(mongo_client)
        )  # TODO delete
        return mongo_client

    def watch(self) -> ChangeStream[Mapping[str, Any]]:
        db = self.__client()[self.database_name]

        return db.watch([{"$match": {"operationType": {"$in": ["insert"]}}}])


@click.command()
@click.option("--mongo-host", type=str, help="Mongo host", default="localhost")
@click.option("--mongo-port", type=int, help="Mongo port", default=27017)
@click.option(
    "--rabbit-mq-host", type=str, help="Rabbit mq host", default="localhost"
)
@click.option(
    "--azure-keyvault-name",
    type=str,
    help="Name of the azure keyvault from which to retrieve secrets",
    required=False,
    default=None,
)
def main(
    mongo_host: str,
    mongo_port: int,
    rabbit_mq_host: str,
    azure_keyvault_name: Optional[str],
) -> None:
    # TODO azure key vault name needed?
    logger.info("CDC service started")

    aqmp_publisher = AqmpPublisher(rabbit_mq_host)
    mongo_cdc = MongoCDC(mongo_host, mongo_port, "data_fetch")

    logger.info("Watching for changes in the database")
    change_stream = mongo_cdc.watch()

    for change in change_stream:
        logger.debug("Change detected {}", change)
        full_document = change["fullDocument"]

        # remove non serializable keys
        del full_document["_id"]

        aqmp_publisher.publish(full_document)

    # TODO add a signal handler to stop the service
    logger.info("CDC service finished")


if __name__ == "__main__":
    main()
