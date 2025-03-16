# 214 Project: Benchmarking with Kafka and Pulsar

## Steps to Set Up Docker
** make sure docker and docker compose is installed (might need docker desktop) **
1. $ cd docker // navigate into docker directory
2. $ docker-compose up -d // sets up the containers
3. $ docker-compose up --build // runs the benchmark script

Just running docker-compose up will combine steps

## Helpful commands:
docker ps --> shows running containers

## For multiple producers and consumers
- Default is 3
- Can dynamically change this by running **docker-compose up --scale pulsar-benchmark=n** where n is the number you want. This will override the yml but please update the Dockerfile
