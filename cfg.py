__author__ = 'netanel'

import logging


LOG_LEVEL = logging.INFO


READING_RESOLUTION = 10  # [S] gather sensors reading every READING_RESOLUTION time
RELAY_DELTA_MEASURE_MS = 10  # [mS] when arelay changes we want to "measure" two points before and after change so we get binary graphs

# shift register controls
SER = 40
RCLK = 38
SRCLK = 36
REGISTER_SIZE = 8

