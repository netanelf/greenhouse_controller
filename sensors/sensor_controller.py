__author__ = 'netanel'

import logging


class SensorController(object):
    """
    all sensor controllers should derive from this class.
    """
    def __init__(self, name):
        self._name = name
        self._last_read = None
        self._logger = logging.getLogger(__name__ + name)

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

