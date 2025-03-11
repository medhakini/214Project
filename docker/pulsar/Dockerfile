# Use a Python base image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (like gcc for compiling any libraries if needed)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (pulsar client and any other required libraries)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the benchmarking scripts
COPY pulsar-benchmark /app/pulsar-benchmark

# Set environment variables (can be overridden in docker-compose.yml)
ENV PULSAR_BROKER=pulsar://localhost:6650
ENV PULSAR_TOPIC=persistent://public/default/my-topic
ENV TIMEOUT=3000
ENV NUM_MESSAGES=1000000
ENV NUM_PRODUCERS=3
ENV NUM_CONSUMERS=3

# Run multiple producers and consumers
# CMD ["bash", "-c", "for i in $(seq 1 $NUM_PRODUCERS); do python /app/pulsar-benchmark/pulsar_producer_stocks.py & done; for i in $(seq 1 $NUM_CONSUMERS); do python /app/pulsar-benchmark/pulsar_consumer_stocks.py & done; wait"]
CMD ["bash", "-c", "for i in $(seq 1 $NUM_PRODUCERS); do python /app/pulsar-benchmark/pulsar_producer_stocks.py & python /app/pulsar-benchmark/pulsar_producer_html.py & done; for i in $(seq 1 $NUM_CONSUMERS); do python /app/pulsar-benchmark/pulsar_consumer_stocks.py & python /app/pulsar-benchmark/pulsar_consumer_html.py & done; wait"]
