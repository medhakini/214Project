FROM python:3.9

WORKDIR /benchmark

COPY benchmark/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY benchmark/ benchmark/

CMD sleep 10 && python benchmark.py  # Wait for Kafka to be ready
