import os
import random
import pulsar
import time
from googlesearch import search
import urllib.request

time.sleep(10)
# requires the docker file to define the broker
broker = os.getenv("PULSAR_BROKER", "pulsar://localhost:6650")

# requires the docker file to define the topic that each producer will write to
# NOTE: In this task, several producers can contribute to the same topic!
topic = os.getenv("PULSAR_TOPIC", "persistent://public/default/my-topic")

# requires the docker file to define the number of messages to produce
num_messages = int(os.getenv('NUM_MESSAGES', 1000000))

# requires the docker file to define the start (offset) of search results to start each producer on
#   This is necessary when several producers contribute to the same topic, so they don't publish duplicated htmls
#   e.g, if each producer publishes 100 messages, then the query_start of producer1 = 0, query_start of producer 2 = 100, query_start of producer 3 = 200, etc...
search_query_start = int(os.getenv('QUERY_START', 0))

# Can be kept the same if you would like
search_query_batch_size = int(os.getenv('QUERY_BATCH_SIZE', 10))    # tells the search engine how many URLs to retrieve at a time
# search_query_pause = int(os.getenv('QUERY_PAUSE', 2))      # tells the search engine to wait 2 seconds between queries to google search. If we make this too small, our IP might be blocked

# requires the docker file to define the country whose news we will scrape
country = os.getenv('QUERY_COUNTRY', "French")
query = f"{country} news"

client = pulsar.Client(broker)
producer = client.create_producer(topic)

# produce messages and send them to the topic
start = time.time()
num_messages_sent = 0
while True:
    for url in search(query, num_results=search_query_batch_size, lang="en", unique=True, region="us", sleep_interval=2):
        try:
            print("trying in producer html")
            fp = urllib.request.urlopen(url.url)
            mybytes = fp.read()

            html_page = mybytes.decode("utf8")
            fp.close()

            producer.send(html_page)
            num_messages_sent += 1
            print("BENCHMARK HTML PRODUCER MESSAGE", num_messages_sent, " TIME:", time.time()-start)
            if num_messages_sent >= num_messages:
                break
            
            time.sleep(0.75)

        except Exception as e:
            print("No access to this webpage, trying the next one...")
    
    if num_messages_sent >= num_messages:
        break

client.close()