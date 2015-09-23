__author__ = 'netanel'

import logging


LOG_LEVEL = logging.DEBUG


READING_RESOLUTION = 10  # [S] gather sensors reading every READING_RESOLUTION time
READING_TIME = 5  # [S] the amount of time after issuing a reading command we could read the new value

DHT22_SENSORS = list()
DHT22_SENSORS.append({'name': 'floor_sensor', 'pin': 4})
DHT22_SENSORS.append({'name': 'door_sensor', 'pin': 5})
DHT22_SENSORS.append({'name': 'ground_sensor', 'pin': 6})
