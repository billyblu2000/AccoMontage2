import os

BASE_DIR_lst = os.path.abspath(__file__).split("/")[:-2]
BASE_DIR = ""
for i in BASE_DIR_lst:
    BASE_DIR += "/"+i
BASE_DIR += "/"
BASE_DIR = BASE_DIR[1:]
STATIC_DIR = BASE_DIR + "static/"
RESOURCE_DIR = BASE_DIR + "resource/"

