__author__ = 'netanel'

import logging
import os
from datetime import timedelta

LOG_LEVEL = logging.DEBUG
DB_RETRIES = 5

SENSOR_READING_RESOLUTION = 10  # [S] gather sensors reading every READING_RESOLUTION time
RELAY_STATE_WRITING_RESOLUTION = 10  # [S] check if wanted state changed, write wanted state to relays
KEEP_ALIVE_RESOLUTION = 10  # [S] send brain keepalive
CONFIGURATION_RESOLUTION = 10  # [S] all other things to do in brain cycle
FLOW_MANAGERS_RESOLUTION = 1  #[S]

RELAY_DELTA_MEASURE_MS = 10  # [mS] when arelay changes we want to "measure" two points before and after change so we get binary graphs
NUM_HISTORY_MEASUREMENTS = 8  # save last x measurement - this can be used for rolling average outliers etc.

# shift register controls
SER = 12
RCLK = 13
SRCLK = 15
ENABLE = 11
REGISTER_SIZE = 8

# DB backupper configurations
DB_BACKUPPER_WAIT_TIME = 10
NUMBER_OF_ITEMS_IN_RPI_DB = 1000*32
NUMBER_OF_ITEMS_TO_MOVE_ONCE = 100

# image capture configurations
RASPISTILL_ARGS = ['-ae', '64,0x00,0x8080FF', '-a', '12'] # ['-vf', '-hf'], flip, etc.

# failures manager configurations
FAILURE_MANAGER_WAIT_TIME = 2
STATISTICS_PRINTING_FREQUENCY = timedelta(minutes=0.2)
FAILURE_INSPECTION_TIME = timedelta(minutes=5)
# amount of times an exception is ok in last FAILURE_INSPECTION_TIME
FAILURE_EXCEPTIONS_CONFIG = \
    {'database is locked': {'times': 3, 'result': 'restart'},
     'integer division or modulo by zero': {'times': 10, 'result': 'restart'},
     "'Brain' object has no attribute 'lcd_alive'": {'times': float('inf'), 'result': None}}

# keep-alive
KEEP_ALIVE_TIMEOUT = timedelta(seconds=60)  # TODO: not used due to importing problems...

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



