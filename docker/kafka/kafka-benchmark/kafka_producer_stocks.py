from kafka import KafkaProducer
import os
import random
import time

# ready_file_path = "/shared/consumer_ready.txt"
# while not os.path.exists(ready_file_path):
#     print("Waiting for consumer to subscribe...")
#     time.sleep(1)

print("I WPKE UP")
# requires the docker file to define the topic that each producer will write to
topic = os.getenv('KAFKA_TOPIC', 'stock_topic')

# requires the docker file to define the broker
broker = os.getenv('KAFKA_BROKER', 'localhost:9092')

# requires the docker file to define the number of messages to produce
num_messages = int(os.getenv('NUM_MESSAGES', 1000000))

# requires the docker file to define the number of partitions for the topic associated with the producer
num_partitions = int(os.getenv('NUM_PARTITIONS', 100))  # Can be anything as long as it's larger than the number of consumers on this topic. Let it be large to be safe

# define producer
producer = KafkaProducer(
    bootstrap_servers=broker,
) # bootstrap_servers is the server corresponding to the kafka broker


# produce messages and send them to the topic
stock_price = max(1, random.random() * 1000) # random stock price greater than 1
for i in range(num_messages):
    if i % 1000 == 0:
        print("SENDING MESSAGE: ", i)
    random_delta = (random.random() - 0.5) * 2 * stock_price / 1000 # a positive or negative fluctuation in the stock price ranging between -0.1% to +0.1% of the stock price

    stock_price = max(1, stock_price + random_delta) # update stock price, but don't let the price reduce below 1
    message = str(stock_price).encode("utf-8")

    partition_key = (i % num_partitions).to_bytes(4, byteorder='big')

    producer.send(topic, key=partition_key, value=message)

producer.flush()
producer.close()