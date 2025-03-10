import os
import pulsar
import fcntl
import time
import os.path
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


time.sleep(20)
# requires the docker file to define the broker
broker = os.getenv("PULSAR_BROKER", "pulsar://localhost:6650")

# requires the docker file to define the topic that each consumer will read from
topic = os.getenv("PULSAR_TOPIC", "persistent://public/default/my-topic")

# requires the docker file to define timeout in ms, which defines how long the consumer will wait after receiving its last message to terminate
timeout = int(os.getenv('TIMEOUT', 3000))

# requires the docker file to define the batch timeout in ms, which defines how long the consumer will wait on a small batch before pulling it anyways
batch_timeout = int(os.getenv('BATCH_TIMEOUT', 3000))

# requires the docker file to define the batch size, which defines how many messages the consumer will wait to collect before pulling them
batch_size = int(os.getenv('BATCH_SIZE', 3000))

client = pulsar.Client(broker)
batch_policy = pulsar.ConsumerBatchReceivePolicy(max_num_message=batch_size, timeout_ms=batch_timeout)
consumer = client.subscribe(topic, subscription_name="my-subscription", consumer_type=pulsar.ConsumerType.Shared, batch_receive_policy=batch_policy)

shared_dir = f"/shared/pulsar"
if not os.path.exists(shared_dir):
    os.makedirs(shared_dir, exist_ok=True)
    
shared_path = f"{shared_dir}/{topic.replace(':', '_').replace('/', '_')}.log"  # make filename safe

# make sure the file exists before opening in r+ mode
if not os.path.exists(shared_path):
    with open(shared_path, "w") as f:
        f.write("0\n")
    print("file created")


nltk.download('vader_lexicon')
sid_obj = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    sentiment_dict = sid_obj.polarity_scores(text)
    return sentiment_dict['compound']

class TimeoutException(Exception):
    pass

last_real_message_time = time.time()

try:
    while True:
        messages = consumer.batch_receive()
        if len(messages) == 0 and time.time() - last_real_message_time > timeout: # timeout exceeded since last real batch
            raise TimeoutException("Timeout exceeded since last real (nonempty) batch") 
        else:
            last_real_message_time = time.time()

        for message in messages:
            message = message.data().decode("utf-8")

            # compute sentiment score
            soup = BeautifulSoup(message, 'html.parser')
            
            content = ""
            for para in soup.find_all("p"): 
                content += para.get_text()

            sentiment_score = analyze_sentiment(content)

            with open(shared_path, "r+") as f:
                # update shared sentiment score
                fcntl.flock(f, fcntl.LOCK_EX)  # Lock file for safe access

                try:
                    lines = f.readlines()  # Read all lines
                    if not lines or len(lines) < 1:
                        shared_sentiment_score = 0
                    else:
                        shared_sentiment_score = float(lines[0].strip())

                    shared_sentiment_score += sentiment_score


                    # Replace first line with new data and write back
                    f.seek(0)
                    f.writelines([f"{shared_sentiment_score}"])
                    f.truncate()  # Remove any leftover content
                except Exception as e:
                    print(f"Error processing file: {e}")
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)  # Unlock file
            
            consumer.acknowledge(message)
except Exception as e:
    print(f"Shutting down pulsar consumer. Error: {e}")
finally:
    client.close()