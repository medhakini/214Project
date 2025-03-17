#!/bin/bash

# Run the first Python script and save its output to a file
python kafka_consumer_stocks.py > output2.txt & python kafka_producer_stocks.py > output1.txt

# Run the second Python script and save its output to another file

#!/bin/bash

# Run the first Python script and save its output to a file
python kafka_producer_html.py > output3.txt & python kafka_consumer_html.py > output4.txt

# Run the second Python script and save its output to another file


# Combine the outputs into a single file
cat output3.txt output4.txt > times11.txt

# Optional: Remove the temporary output files
cat output1.txt output2.txt output3.txt output4.txt > times11.txt
grep -E "BENCHMARK" times11.txt > times12.txt


# Optional: Remove the temporary output files
rm output1.txt output2.txt output3.txt output4.txt
