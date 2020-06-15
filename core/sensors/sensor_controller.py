__author__ = 'netanel'

import logging
from collections import deque
from django.utils import timezone
import cfg


class Measurement(object):
    def __init__(self, time, value, sensor_name):
        self.time = time
        self.value = value
        self.sensor_name = sensor_name

    def __unicode__(self):
        return 'sensor_name: {}, time: {}, value: {}'.format(self.sensor_name, self.time, self.value)

    def __repr__(self):
        return 'sensor_name: {}, time: {}, value: {}'.format(self.sensor_name, self.time, self.value)


class SensorController(object):
    """
    all sensor controllers should derive from this class.
    """
    def __init__(self, name):
        self._name = name
        self._logger = logging.getLogger(name)
        self._history = deque([None] * cfg.NUM_HISTORY_MEASUREMENTS, maxlen=cfg.NUM_HISTORY_MEASUREMENTS)
        self._last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=None)

    def get_name(self) -> str:
        return self._name

    def get_last_read(self) -> Measurement:
        return self._last_read

    def read(self) -> Measurement:
        raise NotImplemented


def history_appender_decorator(func):
    def decorated(self):
        val = func(self)
        self._logger.debug('adding {} to history'.format(val))
        self._history.append(val)
        self._logger.debug('history: {}'.format(self._history))
        return val

    return decorated

# convert between physical pi to GPIO (for Adafruit_DHT that uses GPIO numbering)
# (Physical pin: GPIO number)
GPIO_TO_PIN_TABLE = {
    3: 2,
    5: 3,
    7: 4,
    8: 14,
    10: 15,
    11: 17,
    12: 18,
    13: 27,
    15: 22,
    16: 23,
    18: 24,
    19: 10,
    21: 9,
    22: 25,
    23: 11,
    24: 8,
    26: 7,
    29: 5,
    31: 6,
    32: 12,
    33: 13,
    35: 19,
    36: 16,
    37: 26,
    38: 20,
    40: 21
}


