from pprint import pprint
import logging

from pip._vendor.pep517 import colorlog

AUDIO_OVER_WRITE = False
print = print
SHOW_WARNINGS = True

logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
