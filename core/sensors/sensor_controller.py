__author__ = 'netanel'

import logging


class SensorController(object):
    """
    all sensor controllers should derive from this class.
    """
    def __init__(self, name):
        self._name = name
        self._logger = logging.getLogger(name)

    def get_name(self):
        return self._name

    def read(self):
        """
        issue a reading of the sensor, this is an asynchronous read, the actual reading should be retrieved by using
        get_read()
        :return: None
        """
        self._logger.debug('initiated a read for sensor {}'.format(self._name))

    def get_read(self):
        """
        get the last reading from the sensor
        :return: the last reading or None
        """
        return self._last_read


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


class Measurement(object):
    def __init__(self, time, value, sensor_name):
        self.time = time
        self.value = value
        self.sensor_name = sensor_name

    def __unicode__(self):
        return 'sensor_name: {}, time: {}, value: {}'.format(self.sensor_name, self.time, self.value)