__author__ = 'netanel'

import logging

LOG_LEVEL = logging.DEBUG
DB_RETRIES = 5

READING_RESOLUTION = 10  # [S] gather sensors reading every READING_RESOLUTION time
RELAY_DELTA_MEASURE_MS = 10  # [mS] when arelay changes we want to "measure" two points before and after change so we get binary graphs

# shift register controls
SER = 12
RCLK = 13
SRCLK = 15
ENABLE = 11
REGISTER_SIZE = 8

# DB backupper configurations
NUMBER_OF_ITEMS_IN_RPI_DB = 1000
NUMBER_OF_ITEMS_TO_MOVE_ONCE = 100
DB_BACKUPPER_WAIT_TIME = 10

