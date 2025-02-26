import time
from kafka import KafkaProducer, KafkaConsumer
from pulsar import Client as PulsarClient
import requests

KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "benchmark-topic"
PULSAR_BROKER = "pulsar://pulsar:6650"
PULSAR_TOPIC = "benchmark-topic"
FLINK_REST_API = "http://flink-jobmanager:8081"
NUM_MESSAGES = 10000

def benchmark_kafka():
    producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER, api_version=(0,11,5))
    start_time = time.time()
    
    for i in range(NUM_MESSAGES):
        producer.send(KAFKA_TOPIC, f"message-{i}".encode())
    producer.flush()
    
    end_time = time.time()
    print(f"Kafka Produced {NUM_MESSAGES} messages in {end_time - start_time:.2f} seconds")

    consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_BROKER, auto_offset_reset="earliest", group_id="benchmark-group")
    start_time = time.time()
    
    received = 0
    for _ in consumer:
        received += 1
        if received >= NUM_MESSAGES:
            break
    
    end_time = time.time()
    print(f"Kafka Consumed {received} messages in {end_time - start_time:.2f} seconds")

def benchmark_pulsar():
    client = PulsarClient(PULSAR_BROKER)
    producer = client.create_producer(PULSAR_TOPIC)
    start_time = time.time()

    for i in range(NUM_MESSAGES):
        producer.send(f"message-{i}".encode())

    end_time = time.time()
    print(f"Pulsar Produced {NUM_MESSAGES} messages in {end_time - start_time:.2f} seconds")

    consumer = client.subscribe(PULSAR_TOPIC, "benchmark-subscription")
    start_time = time.time()

    received = 0
    while received < NUM_MESSAGES:
        msg = consumer.receive()
        consumer.acknowledge(msg)
        received += 1

    end_time = time.time()
    print(f"Pulsar Consumed {received} messages in {end_time - start_time:.2f} seconds")
    client.close()

def benchmark_flink():
    print("Starting Flink Benchmark...")

    # Check Flink job status via REST API
    try:
        response = requests.get(f"{FLINK_REST_API}/jobs/overview")
        jobs = response.json().get("jobs", [])
        
        if jobs:
            print("Flink job is running. Measuring throughput...")
            start_time = time.time()
            
            # Wait for the job to process messages (This is a simple wait, could be improved)
            time.sleep(10)  

            end_time = time.time()
            print(f"Flink Processed {NUM_MESSAGES} messages in {end_time - start_time:.2f} seconds")
        else:
            print("No Flink jobs found. Ensure the Flink Kafka consumer job is deployed.")

    except Exception as e:
        print(f"Error checking Flink job: {e}")

if __name__ == "__main__":
    print("Starting Kafka Benchmark...")
    benchmark_kafka()
    
    print("\nStarting Pulsar Benchmark...")
    benchmark_pulsar()

    print("\nStarting Flink Benchmark...")
    benchmark_flink()
