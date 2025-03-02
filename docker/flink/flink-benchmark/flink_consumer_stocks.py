from pyflink.datastream import StreamExecutionEnvironment, SinkFunction
from pyflink.common import CheckpointingMode
import os
import fcntl

# requires the docker file to define the topic that each producer will write to
topic = os.getenv("FLINK_TOPIC", "persistent://public/default/my-topic")

# requires the docker file to define timeout in ms, which defines how long the consumer will wait after receiving its last message to terminate
timeout = int(os.getenv('TIMEOUT', 1000)) / 1000

# this is stupid, but I can't seem to find a good workaround
# requires the docker file to define the number of consumers that share a topic
topic_split = int(os.getenv('topic_split', 1))

shared_path = f"shared/flink/{topic}.log" # all consumers within the same topic share a file to write the moving average

class StockSink(SinkFunction):
    def __init__(self, topic, timeout, shared_path):
        self.topic = topic
        self.timeout = timeout
        self.shared_path = shared_path
        
    def invoke(self, value, context):
        value = float(value.data().decode("utf-8"))

        with open(self.shared_path, "r+") as f:
            # update shared running averages
            fcntl.flock(f, fcntl.LOCK_EX)  # Lock file for safe access

            lines = f.readlines()  # Read all lines
            if not lines:
                running_average_50 = 0
                running_average_200 = 0
            else:
                running_average_50 = lines[0].strip()
                running_average_200 = lines[1].strip()

            running_average_50 = 0.98 * running_average_50 + 0.02 * value
            running_average_200 = 0.995 * running_average_50 + 0.005 * value


            # Replace first line with new data and write back
            f.seek(0)
            f.writelines([f"{running_average_50}\n", f"{running_average_200}\n"])
            f.truncate()  # Remove any leftover content
            fcntl.flock(f, fcntl.LOCK_UN)  # Unlock file

env = StreamExecutionEnvironment.get_execution_environment()
env.enable_checkpointing(10000, CheckpointingMode.EXACTLY_ONCE)
env.set_parallelism(topic_split)
ds = env.from_collection([])  # Placeholder to define the stream
ds.add_sink(StockSink(topic, timeout, shared_path))
env.execute("Flink Consumer")