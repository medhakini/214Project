import os
import pulsar
import fcntl
import time
import os.path

time.sleep(20)
# requires the docker file to define the broker
broker = os.getenv("PULSAR_BROKER", "pulsar://localhost:6650")

# requires the docker file to define the topic that each consumer will read from
topic = os.getenv("PULSAR_TOPIC", "persistent://public/default/my-topic")

# requires the docker file to define timeout in ms, which defines how long the consumer will wait after receiving its last message to terminate
timeout = int(os.getenv('TIMEOUT', 3000))

client = pulsar.Client(broker)
consumer = client.subscribe(topic, subscription_name="my-subscription", consumer_type=pulsar.ConsumerType.Shared)

shared_dir = f"/shared/pulsar"
if not os.path.exists(shared_dir):
    os.makedirs(shared_dir, exist_ok=True)
    
shared_path = f"{shared_dir}/{topic.replace(':', '_').replace('/', '_')}.log"  # make filename safe

# make sure the file exists before opening in r+ mode
if not os.path.exists(shared_path):
    with open(shared_path, "w") as f:
        f.write("0\n0\n")
    print("file created")

try:
    while True:
        message = consumer.receive(timeout_millis=timeout)
        value = float(message.data().decode("utf-8"))
        print("consumer received message")
        print("from consumer:", value)

        with open(shared_path, "r+") as f:
            print("writing to file: ", shared_path)
            # update shared running averages
            fcntl.flock(f, fcntl.LOCK_EX)  # lock file for safe access

            try:
                lines = f.readlines()  # read all lines
                if not lines or len(lines) < 2:
                    running_average_50 = 0
                    running_average_200 = 0
                else:
                    running_average_50 = float(lines[0].strip())
                    running_average_200 = float(lines[1].strip())

                running_average_50 = 0.98 * running_average_50 + 0.02 * value
                running_average_200 = 0.995 * running_average_200 + 0.005 * value

                # replace first line with new data and write back
                f.seek(0)
                f.writelines([f"{running_average_50}\n", f"{running_average_200}\n"])
                f.truncate()  # remove any leftover content
            except Exception as e:
                print(f"Error processing file: {e}")
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)  # always unlock the file!!
                
        consumer.acknowledge(message)
except Exception as e:
    print(f"Shutting down pulsar consumer. Error: {e}")
finally:
    client.close()