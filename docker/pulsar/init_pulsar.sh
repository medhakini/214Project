#!/bin/bash
# init_pulsar.sh

# Wait until Pulsar broker is fully up and ready to accept commands
until nc -z -v -w30 pulsar-broker 6650; do
  echo "Waiting for Pulsar broker to be available..."
  sleep 5
done

# Create the namespace
bin/pulsar-admin namespaces create public/default

# Create the topic
bin/pulsar-admin topics create persistent://public/default/my-topic

echo "Namespace and topic created successfully."
