from typing import List, TypeVar

from bytewax.outputs import DynamicSink, StatelessSinkPartition
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from feature_pipeline.models.data_model import EmbeddedModel

MessageT = TypeVar("MessageT")

EMBEDDING_SIZE = 384  # TODO to constants?


class QdrantSinkPartition(StatelessSinkPartition[EmbeddedModel]):
    def __init__(self, client: QdrantClient):
        self.client = client

    def __get_collection_name(self, model: EmbeddedModel) -> str:
        return f"vector-{model.source}"

    def __create_collection(self, collection_name: str) -> None:
        if not self.client.collection_exists(collection_name):
            logger.info(
                "Qdrant output: creating collection: {}", collection_name
            )
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=EMBEDDING_SIZE, distance=Distance.COSINE
                ),
            )

    def write_batch(self, items: List[EmbeddedModel]) -> None:
        logger.debug("Qdrant sink, writing a batch of size {}", len(items))

        for embedded_model in items:
            collection_name = self.__get_collection_name(embedded_model)
            logger.debug(
                "Qdrant output: writing embedded to collection {}, content: {}",
                collection_name,
                embedded_model.content,
            )
            # Create collection if not exists
            self.__create_collection(collection_name)

            # rozkouskovat embedded model na id, chunk, embedd
            payload_data = embedded_model.to_payload()
            points = list(
                map(
                    lambda enum: PointStruct(
                        id=enum[0],
                        vector=enum[
                            1
                        ].tolist(),  # convert tensor to list of flows
                        payload=payload_data,
                    ),
                    enumerate(embedded_model.embeddings),
                )
            )

            update_result = self.client.upsert(
                collection_name=collection_name, points=points
            )
            logger.debug(
                "Qdrant output: upsert result status: {}, operation_id: {}",
                update_result.status,
                update_result.operation_id,
            )


class QdrantSink(DynamicSink[EmbeddedModel]):
    def __init__(self, client: QdrantClient):
        self.client = client

    def build(
        self, step_id: str, worker_index: int, worker_count: int
    ) -> StatelessSinkPartition[EmbeddedModel]:
        logger.debug(
            "Qdrant sink called, step-id {}, worker-index {}, worker-count {}",
            step_id,
            worker_index,
            worker_count,
        )
        return QdrantSinkPartition(self.client)
