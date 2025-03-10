from kafka import KafkaConsumer
import os
import time
import fcntl
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')
sid_obj = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    sentiment_dict = sid_obj.polarity_scores(text)
    return sentiment_dict['compound']

time.sleep(3)
print("CONSUMER WOKE UP")
# requires the docker file to define the topic that each consumer will read from
topic = os.getenv('KAFKA_TOPIC', 'stock_topic')

# requires the docker file to define the broker
broker = os.getenv('KAFKA_BROKER', 'localhost:9092')

# requires the docker file to define group that this consumer belongs to
group = os.getenv('CONSUMER_GROUP', "consumer-group-1")

# requires the docker file to define timeout in ms, which defines how long the consumer will wait after receiving its last message to terminate
timeout = int(os.getenv('TIMEOUT', 1000)) / 1000  # Convert to seconds

# requires the docker file to define poll interval in ms, which defines how frequently the consumer will poll for a message
poll_interval = int(os.getenv('POLL_INTERVAL', 50))

# requires the docker file to define the batch size, which defines how many messages the consumer will wait to collect before pulling them
batch_size = int(os.getenv('BATCH_SIZE', 5))

# Initialize Kafka consumer
consumer = KafkaConsumer(
    topic,
    bootstrap_servers=broker,
    group_id=group,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    max_poll_records=batch_size
)

shared_path = f"shared/kafka/{topic}.log"  # All consumers within the same topic share a file to write the sentiment score
os.makedirs(os.path.dirname(shared_path), exist_ok=True)
try:
    f = open(shared_path, "x")
    f.close()
except FileExistsError:
    print("File already exists.")

last_message_time = time.time()

start_time = time.time()  # Start time for throughput calculation
message_count = 0

# File path to log throughput
log_file = "consumer_throughput.log"
try:
    while True:
        # Poll for a message from Kafka
        messages = consumer.poll(timeout_ms=poll_interval)

        # Check if any message is received
        if messages:
            print("CURRENT MESSAGE: ", messages)
            for _, message_list in messages.items():
                for message in message_list:
                    if message:
                        soup = BeautifulSoup(message, 'html.parser')
            
                        content = ""
                        for para in soup.find_all("p"): 
                            content += para.get_text()

                        sentiment_score = analyze_sentiment(content)

                        with open(shared_path, "r+") as f:
                            # Lock the file for safe access
                            fcntl.flock(f, fcntl.LOCK_EX)

                            lines = f.readlines()  # Read all lines
                            if not lines:
                                shared_sentiment_score = 0
                            else:
                                shared_sentiment_score = float(lines[0].strip())

                            # Update the running averages
                            shared_sentiment_score += sentiment_score


                            # Replace first line with new data and write back
                            f.seek(0)
                            f.writelines([f"{shared_sentiment_score}"])
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

time.sleep(600)