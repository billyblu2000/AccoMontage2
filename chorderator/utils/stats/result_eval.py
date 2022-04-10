import json
import os

import numpy as np
import matplotlib.pyplot as plt

RESULT_DIR = "/Users/johnnyhu/PycharmProjects/Chorderator/output/"
dict = {}

for result in os.listdir(RESULT_DIR):
    data = os.path.join(RESULT_DIR, result)
    for file in os.listdir(data):
        if file.split('.')[-1] == 'json':
            with open(os.path.join(data, file), 'r') as f:
                temp = json.load(f)
                for i in temp:
                    id = i['duplicate_id']
                    try:
                        dict[id] += 1
                    except:
                        dict[id] = 1


dict = {k: v for k, v in sorted(dict.items(), key=lambda item: item[1], reverse=True)}
print(dict)
occurs = list(dict.values())
index = list(str(i) for i in dict.keys())
plt.bar(index, occurs)
plt.show()