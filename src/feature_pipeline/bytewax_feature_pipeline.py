import bytewax.operators as op
from bytewax.dataflow import Dataflow
from kombu import Connection  # type: ignore
from loguru import logger
from qdrant_client import QdrantClient

from feature_pipeline.data_flow.stream_input import AmqpSource
from feature_pipeline.data_flow.stream_output import QdrantSink
from feature_pipeline.data_logic.dispatchers import (
    ChunkingDataHandler,
    EmbedingFactory,
    InputDataCleaningHandler,
    InputMessageFactory,
)

# *** Feature streaming pipeline flow ***
logger.info("Hello from feature pipeline")

# TODO move me to settings
embedding_model_id = "BAAI/bge-small-en-v1.5"
embedding_model_max_input_length = 512

ipnut_message_factory = InputMessageFactory()
data_chunk_handler = ChunkingDataHandler(
    embedding_model_id, embedding_model_max_input_length
)
data_embedd_dispatcher = EmbedingFactory()

# 1. read data from queue
flow = Dataflow("feature-pipeline")

# 2. map input to pydantic models
rabbit_mq_connection = Connection("amqp://localhost//")
stream_in = op.input("input", flow, AmqpSource(rabbit_mq_connection))

data_fetch = op.map(
    "fetch", stream_in, ipnut_message_factory.create_input_message
)

# 3. apply data specific cleaning
cleaning_handler = InputDataCleaningHandler()
data_clean = op.map("clean", data_fetch, cleaning_handler.clean)

# 4. chunk the data and flatten them to 1D list
data_chunk = op.map("chunk", data_clean, data_chunk_handler.chunk_data_model)

# 5. embed the chunks
data_embedd = op.map("embedd", data_chunk, data_embedd_dispatcher.create)

# 6. load vectors to quadrant
qdrant_client = QdrantClient(host="localhost", port=6333)
op.output("sink-qdrant", data_embedd, QdrantSink(qdrant_client))
