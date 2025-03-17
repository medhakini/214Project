import random
import matplotlib.pyplot as plt
import numpy as np

stock_prod_sent = {}
stock_cons_rec = {}
html_prod_sent = {}
html_cons_rec = {}
stock_latencies = []
html_latencies = []

with open("times12.txt", "r") as f:
    for l in f:
        l = l.split(" ")
        if l[1] == "HTML": print(l)
        if l[1] == "STOCK" and l[2] == "CONSUMER":
            try:
                t = float(l[7][:-2])
                stock_cons_rec[l[4]] = t
            except:
                pass
        elif l[1] == "STOCK" and l[2] == "PRODUCER":
            try:
                t = float(l[7][:-2])
                stock_prod_sent[l[4]] = t
            except:
                pass
        elif l[1] == "HTML" and l[2] == "CONSUMER":
            try:
                t = float(l[7][:-2])
                html_cons_rec[l[4]] = t
            except:
                pass
        elif l[1] == "HTML" and l[2] == "PRODUCER":
            try:
                t = float(l[7][:-2])
                html_prod_sent[l[4]] = t
            except:
                pass

for i in stock_cons_rec:
    if i in stock_prod_sent:
        stock_latencies.append(stock_cons_rec[i] - stock_prod_sent[i])
for i in html_cons_rec:
    if i in html_prod_sent:
        html_latencies.append(html_cons_rec[i] - html_prod_sent[i])
print(html_cons_rec)
    # if int(i) > 5 and str(int(i)-5) in html_cons_rec:
    #     html_latencies.append(html_cons_rec[i] + random.randint(1, 100) - html_cons_rec[str(int(i)-5)])

print("AVG STOCK LATENCY:", sum(stock_latencies)/len(stock_latencies))
print("COUNT STOCK LATENCY:", len(stock_latencies))
print("MAX STOCK LATENCY:", max(stock_latencies))
print("AVG HTML LATENCY:", sum(html_latencies)/len(html_latencies))
print("COUNT HTML LATENCY:", len(html_latencies))
print("MAX HTML LATENCY:", max(html_latencies))

plt.hist(html_latencies, bins=100, alpha=0.5, label='html', edgecolor='black', density=True)
plt.ylabel('Latency ms')
plt.xlabel('Frequency')
plt.title('Histogram')
plt.savefig("html.png")


plt.hist(stock_latencies, bins=20, alpha=0.5, label='stock', edgecolor='black', density=True)
plt.ylabel('Latency ms')
plt.xlabel('Frequency')
plt.title('Histogram')
plt.savefig("stock.png")