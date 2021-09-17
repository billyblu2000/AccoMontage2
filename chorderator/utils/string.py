import os

BASE_DIR_lst = os.path.abspath(__file__).split("/")[:-2]
PROJECT_DIR_lst = os.path.abspath(__file__).split("/")[:-3]
BASE_DIR = ""
for i in BASE_DIR_lst:
    BASE_DIR += "/"+i
PROJECT_DIR = ""
for i in PROJECT_DIR_lst:
    PROJECT_DIR += "/"+i
BASE_DIR += "/"
BASE_DIR = BASE_DIR[1:]
PROJECT_DIR += "/"
PROJECT_DIR = PROJECT_DIR[1:]
STATIC_DIR = BASE_DIR + "static/"
RESOURCE_DIR = PROJECT_DIR + "resource/"

