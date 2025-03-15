# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY kafka-benchmark/requirements.txt requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the producer and consumer scripts
# COPY kafka-benchmark/kafka_producer_stocks.py kafka_producer_stocks.py
# COPY kafka-benchmark/kafka_consumer_stocks.py kafka_consumer_stocks.py
COPY kafka-benchmark /app/kafka-benchmark
# Ensure shared folder for cross-container data
RUN mkdir -p /shared/kafka

# Environment variables for flexibility
ENV KAFKA_TOPIC=stock_topic
ENV KAFKA_BROKER=kafka:9092
ENV NUM_MESSAGES=1000000
ENV NUM_PARTITIONS=100
ENV TIMEOUT=1000
ENV POLL_INTERVAL=50

ENV KAFKA_TOPIC= stock_topic
ENV KAFKA_BROKER= kafka:9092
ENV NUM_PARTITIONS= 1

ENV NUM_CONSUMERS= 1
ENV NUM_PRODUCERS= 1
ENV CONSUMER_GROUP= consumer-group-1
ENV POLL_INTERVAL= 50

CMD ["bash", "-c", "for i in $(seq 1 $NUM_PRODUCERS); do python /app/kakfa-benchmark/kafka_producer_stocks.py & done; for i in $(seq 1 $NUM_CONSUMERS); do python /app/kafka-benchmark/kafka_consumer_stocks.py & done; wait"]

