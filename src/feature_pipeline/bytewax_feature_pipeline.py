import bytewax.operators as op
from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow
from bytewax.tracing import setup_tracing
from kombu import Connection
from loguru import logger

from feature_pipeline.data_flow.stream_input import AmqpSource
from feature_pipeline.data_logic.dispatchers import DebugDispatcher

setup_tracing(log_level="DEBUG")

# *** Feature streaming pipeline flow ***
logger.info("Hello from feature pipeline")

# 1. read data from queue
flow = Dataflow("feature-pipeline")

# 2. map input to pydantic models
rabbit_mq_connection = Connection("amqp://localhost//")
stream = op.input("input", flow, AmqpSource(rabbit_mq_connection))
#stream = op.input("input", flow, TestingSource(range(10)))
_ = op.inspect("hello", stream)
# 3. apply data specific cleaning
from_debug = op.map("debug", stream, DebugDispatcher.debug_message)

# 4. load cleaned data to vector db
# 5. chunk the data and flatten them to 1D list
# 6. embed the chunks
# 7. load vectors to quadrant
op.output("out", stream, StdOutSink())
