#!/bin/bash

# Run the first Python script and save its output to a file
python kafka_producer_html.py > output1.txt

python kafka_consumer_html.py > output2.txt

# Combine the outputs into a single file
cat output1.txt output2.txt > times11.txt

# Optional: Remove the temporary output files
rm output1.txt output2.txt
