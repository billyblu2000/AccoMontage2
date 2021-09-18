import logging

AUDIO_OVER_WRITE = False
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '@Chorderator %(asctime)s - %(levelname)s - %(message)s'

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
