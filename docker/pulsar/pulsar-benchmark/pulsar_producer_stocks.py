import os
import random
import pulsar
import time

time.sleep(10)
# requires the docker file to define the broker
broker = os.getenv("PULSAR_BROKER", "pulsar://localhost:6650")

# requires the docker file to define the topic that each producer will write to
topic = os.getenv("PULSAR_TOPIC", "persistent://public/default/my-topic")

# requires the docker file to define the number of messages to produce
num_messages = int(os.getenv('NUM_MESSAGES', 1000000))

client = pulsar.Client(broker)
producer = client.create_producer(topic)

# produce messages and send them to the topic
stock_price = max(1, random.random() * 1000) # random stock price greater than 1
for i in range(num_messages):
    random_delta = (random.random() - 0.5) * 2 * stock_price / 1000 # a positive or negative fluctuation in the stock price ranging between -0.1% to +0.1% of the stock price

    stock_price = max(1, stock_price + random_delta) # update stock price, but don't let the price reduce below 1

    message = str(stock_price).encode("utf-8")
    print("from producer:", message)
    
    producer.send(message)
    print("producer sent message")

client.close()