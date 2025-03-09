# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements and install dependencies
COPY kafka-benchmark/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the producer and consumer scripts
COPY kafka-benchmark/kafka_producer_stocks.py kafka_producer_stocks.py
COPY kafka-benchmark/kafka_consumer_stocks.py kafka_consumer_stocks.py

# Ensure shared folder for cross-container data
RUN mkdir -p /shared/kafka

# Environment variables for flexibility
ENV KAFKA_TOPIC=stock_topic
ENV KAFKA_BROKER=localhost:9092
ENV NUM_MESSAGES=1000000
ENV NUM_PARTITIONS=100
ENV CONSUMER_GROUP=1
ENV TIMEOUT=1000
ENV POLL_INTERVAL=50

# Default command to keep container running — overridden by docker-compose.yml
CMD ["sleep", "infinity"]
