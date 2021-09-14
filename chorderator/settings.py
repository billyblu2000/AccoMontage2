import logging

AUDIO_OVER_WRITE = False
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
