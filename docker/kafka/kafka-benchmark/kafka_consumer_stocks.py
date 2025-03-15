from kafka import KafkaConsumer
import os
import time
import fcntl

print("CONSUMER WOKE UP")
# requires the docker file to define the topic that each consumer will read from
topic = os.getenv('KAFKA_TOPIC', 'stock_topic')

# requires the docker file to define the broker
broker = os.getenv('KAFKA_BROKER', 'localhost:9092')

# requires the docker file to define group that this consumer belongs to
group = os.getenv('CONSUMER_GROUP', "consumer-group-1")

# requires the docker file to define timeout in ms, which defines how long the consumer will wait after receiving its last message to terminate
timeout = int(os.getenv('TIMEOUT', 1000))  # Convert to seconds

# requires the docker file to define poll interval in ms, which defines how frequently the consumer will poll for a message
poll_interval = int(os.getenv('POLL_INTERVAL', 50))

def on_assign(consumer, partitions):
    print("Consumer subscribed to partitions:", partitions)
    ready_file_path = "/shared/consumer_ready.txt"
    with open(ready_file_path, "w") as f:
        f.write("Ready")

# Initialize Kafka consumer
consumer = KafkaConsumer(
    topic,
    bootstrap_servers="kafka:9092",
    group_id=group,
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

shared_path = f"shared/kafka/{topic}.log"  # All consumers within the same topic share a file to write the moving average
os.makedirs(os.path.dirname(shared_path), exist_ok=True)
try:
    f = open(shared_path, "x")
    f.close()
except FileExistsError:
    print("File already exists.")

last_message_time = time.time()

# on_assign(consumer, 10)

start_time = time.time()  # Start time for throughput calculation
message_count = 0

# File path to log throughput
log_file = "consumer_throughput.log"
try:
    while True:
        # Poll for a message from Kafka
        messages = consumer.poll(timeout_ms=poll_interval, max_records=1)

        # Check if any message is received
        if messages:
            # Extract the first message from the topic-partition dictionary
            for _, message_list in messages.items():
                message = message_list[0]
                if message:
                    value = float(message.value.decode("utf-8"))
                    print(message)
                    with open(shared_path, "r+") as f:
                        # Lock the file for safe access
                        fcntl.flock(f, fcntl.LOCK_EX)

                        lines = f.readlines()  # Read all lines
                        if not lines:
                            running_average_50 = 0
                            running_average_200 = 0
                        else:
                            running_average_50 = float(lines[0].strip())
                            running_average_200 = float(lines[1].strip())

                        # Update the running averages
                        running_average_50 = 0.98 * running_average_50 + 0.02 * value
                        running_average_200 = 0.995 * running_average_200 + 0.005 * value

                        # Replace first line with new data and write back
                        f.seek(0)
                        f.writelines([f"{running_average_50}\n", f"{running_average_200}\n"])
                        f.truncate()  # Remove any leftover content
                        fcntl.flock(f, fcntl.LOCK_UN)  # Unlock the file

                    last_message_time = time.time()  # Reset timer on new message

        else:
            # Check if the inactivity timeout has been exceeded
            if time.time() - last_message_time > timeout:
                print("Inactivity timeout exceeded. Terminating consumer.")
                break

except KeyboardInterrupt:
    print(f"Shutting down consumer {group}.")
finally:
    consumer.close()