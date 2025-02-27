from kafka import KafkaConsumer
import os
import time
import fcntl

# requires the docker file to define the topic that each consumer will read from
topic = os.getenv('KAFKA_TOPIC', 'default_topic')

# requires the docker file to define the broker
broker = os.getenv('KAFKA_BROKER', 'localhost:9092')

# requires the docker file to define group that this consumer belongs to
group = int(os.getenv('CONSUMER_GROUP', 1))

# requires the docker file to define timeout in ms, which defines how long the consumer will wait after receiving its last message to terminate
timeout = int(os.getenv('TIMEOUT', 1000)) / 1000

# requires the docker file to define poll interval in ms, which defines how frequenctly the consumer will poll for a message
poll_interval = int(os.getenv('POLL_INTERVAL', 50))

# Initialize Kafka consumer
consumer = KafkaConsumer(
    topic,
    bootstrap_servers=broker,
    group_id=group,
    auto_offset_reset='earliest'
    enable_auto_commit=True
)


shared_path = f"shared/kafka/{topic}.log" # all consumers within the same topic share a file to write the moving average
os.makedirs(os.path.dirname(shared_path), exist_ok=True)

last_message_time = time.time()

try:
    while True:
        message = consumer.poll(timeout_ms=poll_interval, max_records=1)
        value = float(message.value.decode("utf-8"))

        if message:
            with open(shared_path, "r+") as f:
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


            last_message_time = time.time()  # Reset timer on new message

        else:
            # Check if the inactivity timeout has been exceeded
            if time.time() - last_message_time > timeout:
                break

except KeyboardInterrupt:
    print(f"Shutting down consumer {id}.")
finally:
    consumer.close()