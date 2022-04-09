import json
import os

import numpy as np

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
print(dict)