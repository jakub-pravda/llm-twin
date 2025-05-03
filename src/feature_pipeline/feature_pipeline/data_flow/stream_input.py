from typing import Any, Dict, Iterable, List

from bytewax.inputs import (
    DynamicSource,
    StatelessSourcePartition,
)
from kombu import Connection, Exchange, Message, Queue  # type: ignore
from loguru import logger

AmqpMessageBody = Dict[str, Any]


class AmqpPartition(StatelessSourcePartition[AmqpMessageBody]):
    def __init__(self, amqp_connection: Connection):
        self.amqp_connection = amqp_connection

        # TODO move it to share
        self.feature_pipeline_exchange = Exchange(
            "feature_pipeline", type="direct"
        )
        self.feature_pipeline_routing_key = "feature_pipeline"
        self.feature_pipeline_queue = Queue(
            "feature_pipeline",
            exchange=self.feature_pipeline_exchange,
            routing_key=self.feature_pipeline_routing_key,
        )

        self.current_batch: List[AmqpMessageBody] = []
        self.batch_message_limit = 100

    def __amqp_process_message(
        self, body: AmqpMessageBody, message: Message
    ) -> None:
        logger.debug(
            "AMQP queue: message received: {} with content {}", message, body
        )
        self.current_batch.append(body)
        message.ack()

    def next_batch(self) -> Iterable[AmqpMessageBody]:
        self.current_batch.clear()
        batch_message_count = 0

        with self.amqp_connection.Consumer(
            self.feature_pipeline_queue, callbacks=[self.__amqp_process_message]
        ) as _:
            while batch_message_count < self.batch_message_limit:
                logger.debug("AMQP queue: waiting for next message")
                try:
                    self.amqp_connection.drain_events(timeout=10)
                except TimeoutError as e:
                    logger.debug(
                        "AMQP queue: timeout waiting for message: {}", e
                    )
                    break

        return self.current_batch


class AmqpSource(DynamicSource[AmqpMessageBody]):
    def __init__(self, amqp_connection: Connection):
        self.amqp_connection = amqp_connection

    def list_parts(self) -> List[str]:
        return ["single partition"]

    def build(
        self, step_id: str, worker_index: int, worker_count: int
    ) -> StatelessSourcePartition[AmqpMessageBody]:
        logger.debug(
            "Partition info - step_id:: {}, worker_index: {}, worker_count: {}",
            step_id,
            worker_index,
            worker_count,
        )
        return AmqpPartition(self.amqp_connection)
