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
        self._logger.info('initiated a read for sensor {}'.format(self._name))

    def get_read(self):
        """
        get the last reading from the sensor
        :return: the last reading or None
        """
        return self._last_read


class Measurement(object):
    def __init__(self, time, value, sensor_name):
        self.time = time
        self.value = value
        self.sensor_name = sensor_name

    def __unicode__(self):
        return 'sensor_name: {}, time: {}, value: {}'.format(self.sensor_name, self.time, self.value)