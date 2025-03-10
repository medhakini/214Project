from kafka import KafkaProducer
import os
import random
import time
from googlesearch import search
import urllib.request

time.sleep(3)
print("I WPKE UP")
# requires the docker file to define the topic that each producer will write to
topic = os.getenv('KAFKA_TOPIC', 'stock_topic')

# requires the docker file to define the broker
broker = os.getenv('KAFKA_BROKER', 'localhost:9092')

# requires the docker file to define the number of messages to produce
num_messages = int(os.getenv('NUM_MESSAGES', 1000000))

# requires the docker file to define the number of partitions for the topic associated with the producer
num_partitions = int(os.getenv('NUM_PARTITIONS', 100))  # Can be anything as long as it's larger than the number of consumers on this topic. Let it be large to be safe

# requires the docker file to define the start (offset) of search results to start each producer on
#   This is necessary when several producers contribute to the same topic, so they don't publish duplicated htmls
#   e.g, if each producer publishes 100 messages, then the query_start of producer1 = 0, query_start of producer 2 = 100, query_start of producer 3 = 200, etc...
search_query_start = int(os.getenv('QUERY_START', 0))

# Can be kept the same if you would like
search_query_batch_size = int(os.getenv('QUERY_BATCH_SIZE', 10))    # tells the search engine how many URLs to retrieve at a time
search_query_pause = int(os.getenv('QUERY_PAUSE', 2))      # tells the search engine to wait 2 seconds between queries to google search. If we make this too small, our IP might be blocked

# requires the docker file to define the country whose news we will scrape
country = os.getenv('QUERY_COUNTRY', "Spain")
query = f"{country} news"


# define producer
producer = KafkaProducer(
    bootstrap_servers=broker,
) # bootstrap_servers is the server corresponding to the kafka broker



# produce messages and send them to the topic
num_messages_sent = 0
for url in search(query, num=search_query_batch_size, start=search_query_start, pause=search_query_pause, lang="en", country="us"):
    try:
        fp = urllib.request.urlopen(url)
        mybytes = fp.read()

        html_page = mybytes.decode("utf8")
        fp.close()

        partition_key = (num_messages_sent % num_partitions).to_bytes(4, byteorder='big')

        producer.send(topic, key=partition_key, value=html_page)
        num_messages_sent += 1
        if num_messages_sent >= num_messages:
            break

    except Exception as e:
        print("No access to this webpage, trying the next one...")

# Ensure all messages are sent before exiting
producer.flush()

time.sleep(600)
producer.close()