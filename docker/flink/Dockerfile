# Use the official Flink image, which already has Java and Flink installed
FROM flink:1.16-scala_2.12

# Set environment variables
ENV FLINK_TOPIC=default_topic
ENV NUM_MESSAGES=1000000
ENV TIMEOUT=1000
ENV topic_split=1

# Install Python and PyFlink
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install PyFlink
RUN pip3 install pyflink

# Set the working directory inside the container
WORKDIR /app

# Copy the producer and consumer scripts into the container
COPY flink-benchmark/ /app/

# Make sure the scripts are executable
RUN chmod +x flink_consumer_stocks.py flink_producer_stocks.py

# Set up the entrypoint to run both scripts concurrently
CMD ["sh", "-c", "python3 flink_producer_stocks.py & python3 flink_consumer_stocks.py"]
