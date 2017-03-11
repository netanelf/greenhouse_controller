__author__ = 'netanel'

import logging
import os
from datetime import timedelta

LOG_LEVEL = logging.DEBUG
DB_RETRIES = 5

READING_RESOLUTION = 30  # [S] gather sensors reading every READING_RESOLUTION time
RELAY_DELTA_MEASURE_MS = 10  # [mS] when arelay changes we want to "measure" two points before and after change so we get binary graphs
NUM_HISTORY_MEASUREMENTS = 8  # save last 3 measurement - this can be used for rolling average outliers etc.

# shift register controls
SER = 12
RCLK = 13
SRCLK = 15
ENABLE = 11
REGISTER_SIZE = 8

# DB backupper configurations
NUMBER_OF_ITEMS_IN_RPI_DB = 1000*32
NUMBER_OF_ITEMS_TO_MOVE_ONCE = 100
DB_BACKUPPER_WAIT_TIME = 10

# image capture configurations
IMAGE_CAPTURE_WAIT_TIME = 10  # thread cycle time
IMAGE_FREQUENCY = timedelta(hours=4)
IMAGE_LUX_THRESHOLD = 25  # if lux reading is below threshold disallow image captures


# Dbmover configurations (not used?)
LOCAL_BACKUP_DB_PATH = os.path.join(os.path.dirname(__file__),
                                    'web',
                                    'greenhouse_django_project',
                                    'backup.sqlite3')


# this should probably point to the used DB in the PC side
REMOTE_BACKUP_DB_PATH = os.path.join(os.path.dirname(__file__),
                                    'web',
                                    'greenhouse_django_project',
                                    'remote',
                                    'db.sqlite3')



