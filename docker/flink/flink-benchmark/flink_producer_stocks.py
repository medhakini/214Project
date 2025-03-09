from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import ParallelSourceFunction
from pyflink.common import CheckpointingMode
import random
import os

# requires the docker file to define the topic that each producer will write to
topic = os.getenv("FLINK_TOPIC", "default_topic")

# requires the docker file to define the number of messages to produce
num_messages = int(os.getenv('NUM_MESSAGES', 1000000))

class StockSource(ParallelSourceFunction):
    def __init__(self, topic, num_messages):
        self.topic = topic
        self.num_messages = num_messages

    def run(self, ctx):
        stock_price = max(1, random.random() * 1000) # random stock price greater than 1
        for i in range(self.num_messages):
            random_delta = (random.random() - 0.5) * 2 * stock_price / 1000 # a positive or negative fluctuation in the stock price ranging between -0.1% to +0.1% of the stock price

            stock_price = max(1, stock_price + random_delta) # update stock price, but don't let the price reduce below 1

            message = str(stock_price).encode("utf-8")
            ctx.collect((topic, message))

    def cancel(self):
        pass

env = StreamExecutionEnvironment.get_execution_environment()

env.enable_checkpointing(10000, CheckpointingMode.EXACTLY_ONCE)
ds = env.add_source(StockSource(topic, num_messages)).map(lambda x: x[1])  # Extract value
ds.print()  # For debugging
env.execute("Flink Producer")