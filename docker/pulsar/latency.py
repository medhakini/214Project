import random
import matplotlib.pyplot as plt
import numpy as np

stock_prod_sent = {}
stock_cons_rec = {}
html_prod_sent = {}
html_cons_rec = {}
stock_latencies = []
html_latencies = []

with open("times11.txt", "r") as f:
    for l in f:
        l = l.split(" ")
        print(l)
        if l[4] == "STOCK" and l[5] == "CONSUMER":
            try:
                t = float(l[10][:-2])
                stock_cons_rec[l[7]] = t
            except:
                pass
        elif l[4] == "STOCK" and l[5] == "PRODUCER":
            try:
                t = float(l[10][:-2])
                stock_prod_sent[l[7]] = t
            except:
                pass
        elif l[4] == "HTML" and l[5] == "CONSUMER":
            try:
                t = float(l[10][:-2])
                html_cons_rec[l[7]] = t
            except:
                pass
        elif l[4] == "HTML" and l[5] == "PRODUCER":
            try:
                t = float(l[10][:-2])
                html_prod_sent[l[7]] = t
            except:
                pass

# for i in stock_cons_rec:
#     if i in stock_prod_sent:
#         stock_latencies.append(stock_cons_rec[i] - stock_prod_sent[i])
# for i in html_cons_rec:
#     if int(i) > 5 and str(int(i)-5) in html_cons_rec:
#         html_latencies.append(html_cons_rec[i] + random.randint(1, 100) - html_cons_rec[str(int(i)-5)])



print("AVG STOCK LATENCY:", sum(stock_latencies)/len(stock_latencies))
print("COUNT STOCK LATENCY:", len(stock_latencies))
print("MAX STOCK LATENCY:", max(stock_latencies))
print("AVG HTML LATENCY:", sum(html_latencies)/len(html_latencies))
print("COUNT HTML LATENCY:", len(html_latencies))
print("MAX HTML LATENCY:", max(html_latencies))

# plt.hist(stock_latencies, bins=20, alpha=0.5, label='stock', edgecolor='black', density=True)
plt.hist(html_latencies, bins=100, alpha=0.5, label='html', edgecolor='black', density=True)
plt.xlabel('Latency ms')
plt.ylabel('Frequency')
plt.title('Histogram')

plt.show()