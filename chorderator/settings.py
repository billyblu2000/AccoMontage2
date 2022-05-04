import logging
import os

LOG_LEVEL = logging.INFO
LOG_FORMAT = '@Chorderator %(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

PROJECT_DIR = "/".join(os.path.abspath(__file__).replace('\\', '/').split("/")[:-2]) + '/'
BASE_DIR = PROJECT_DIR + "chorderator/"
STATIC_DIR = BASE_DIR + "static/"
ACCOMONTAGE_DATA_DIR = STATIC_DIR[:-1]
RESOURCE_DIR = PROJECT_DIR + "resource/"

static_storage = {
    'lib': STATIC_DIR + 'source_base.pnt',
    'trans': STATIC_DIR + 'transition_score.mdch',
    'concat_major': STATIC_DIR + 'major_score.mdch',
    'concat_minor': STATIC_DIR + 'minor_score.mdch',
    'dict': STATIC_DIR + 'dict.pcls',
    'rep': STATIC_DIR + 'representatives.pcls',
}

MAXIMUM_CORES = 3
