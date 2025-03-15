from kafka import KafkaProducer
import os
import random
import time
from googlesearch import search
import urllib.request
import sys

print("I WPKE UP")
# requires the docker file to define the topic that each producer will write to
topic = os.getenv('KAFKA_TOPIC', 'html_topic')

# requires the docker file to define the broker
broker = os.getenv('KAFKA_BROKER', 'kafka:9092')

# requires the docker file to define the number of messages to produced
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
country = os.getenv('QUERY_COUNTRY', "Ukraine")
query = f"{country} news"

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
# define producer
producer = KafkaProducer(
    bootstrap_servers=broker
) # bootstrap_servers is the server corresponding to the kafka broker



# produce messages and send them to the topic
num_messages_sent = 0
for url in search(query, num_results=search_query_batch_size,lang="en", unique=True, region="us", sleep_interval=2):
    html_page = b"a" * 1000
    try:
        print(url)
        request = urllib.request.Request(url, headers={'User-Agent': user_agent})
        fp = urllib.request.urlopen(request)
        mybytes = fp.read()

        html_page = mybytes.decode("utf8")
        print(f"Message size: {sys.getsizeof(html_page)} bytes")
        fp.close()
    except Exception as e:
        print("No access to this webpage, trying the next one...")
        print(e)
    try:
        if html_page == b"a" * 1000:
            print("default message sent")
        partition_key = (num_messages_sent % num_partitions).to_bytes(4, byteorder='big')
        producer.send(topic, key=partition_key, value=html_page)
        num_messages_sent += 1
        if num_messages_sent >= num_messages:
            break
    except Exception as e:
        print("couldn't send to consumer..")
        print(e)
    time.sleep(0.5)

# Ensure all messages are sent before exiting
producer.flush()
producer.close()