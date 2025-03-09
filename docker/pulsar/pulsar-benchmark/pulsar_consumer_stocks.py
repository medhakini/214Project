import os
import pulsar
import fcntl

sleep(10)
# requires the docker file to define the broker
broker = os.getenv("PULSAR_BROKER", "pulsar://localhost:6650")

# requires the docker file to define the topic that each consumer will read from
topic = os.getenv("PULSAR_TOPIC", "persistent://public/default/my-topic")

# requires the docker file to define timeout in ms, which defines how long the consumer will wait after receiving its last message to terminate
timeout = int(os.getenv('TIMEOUT', 1000)) / 1000

client = pulsar.Client(broker)
consumer = client.subscribe(topic, subscription_name="my-subscription", consumer_type=pulsar.ConsumerType.Shared)

shared_path = f"shared/pulsar/{topic}.log" # all consumers within the same topic share a file to write the moving average

try:
    while True:
        print("consumer waiting")
        message = consumer.receive(timeout_millis=timeout) # will block until message is received, or throw exception if timeout occurs before then
        value = float(message.data().decode("utf-8"))
        print("consumer received message")
        print("from consumer:", value)

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
            consumer.acknowledge(message)
            fcntl.flock(f, fcntl.LOCK_UN)  # Unlock file
except Exception:
    print(f"Shutting down pulsar consumer.")
finally:
    client.close()