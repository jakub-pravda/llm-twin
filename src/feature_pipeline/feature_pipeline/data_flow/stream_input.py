import json
from typing import Iterable, List, Optional, TypeVar

from bytewax.inputs import FixedPartitionedSource, StatefulSourcePartition
from kombu import Connection, Exchange, Queue  # type: ignore
from loguru import logger

DataT = TypeVar("DataT")
MessageT = TypeVar("MessageT")

class AmqpPartition(StatefulSourcePartition[DataT, MessageT]):

    def __init__(self, amqp_connection: Connection):
        self.amqp_connection = amqp_connection

        # TODO move it to share
        self.feature_pipeline_exchange = Exchange("feature_pipeline", type="direct")
        self.feature_pipeline_routing_key = "feature_pipeline"
        self.feature_pipeline_queue = Queue('feature_pipeline', exchange=self.feature_pipeline_exchange, routing_key=self.feature_pipeline_routing_key)

        self.current_batch = []
        self.batch_message_limit = 100

    def __amqp_process_message(self, body, message):
        logger.debug("AMQP queue - message received: {} with content {}", message, body)
        self.current_batch.append(body)
        message.ack()

    def next_batch(self) -> Iterable[DataT]:
        self.current_batch.clear()
        batch_message_count = 0

        with self.amqp_connection.Consumer(self.feature_pipeline_queue, callbacks=[self.__amqp_process_message]) as consumer:
            while batch_message_count < self.batch_message_limit:
                logger.debug("AMQP queue - waiting for next message")
                try:
                    self.amqp_connection.drain_events(timeout=10)
                except TimeoutError as e:
                    logger.debug("AMQP queue - timeout waiting for message: {}", e)
                    break
    
        return self.current_batch

    def snapshot(self) -> MessageT:
        logger.debug("Snapshot called")
        raise NotImplementedError


class AmqpSource(FixedPartitionedSource[DataT, MessageT]):
    def __init__(self, amqp_connection: Connection):
        self.amqp_connection = amqp_connection

    def list_parts(self) -> List[str]:
        return ["single partition"]

    def build_part(
        self,
        step_id: str,
        for_part: str,
        resume_state: Optional[MessageT],
    ) -> StatefulSourcePartition[DataT, MessageT]:
        logger.debug("Partition info - step_id:: {}, for_part: {}, resume_state: {}", step_id, for_part, resume_state)
        return AmqpPartition(self.amqp_connection)
