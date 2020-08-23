__author__ = 'netanel'
import logging
from datetime import datetime
from core.sensors.sensor_controller import GPIO_TO_PIN_TABLE
try:
    import Adafruit_DHT as dht
except Exception:
    pass

import cfg


'''
def read_retry(sensor, pin, retries=15, delay_seconds=2, platform=None):
    """Read DHT sensor of specified sensor type (DHT11, DHT22, or AM2302) on
    specified pin and return a tuple of humidity (as a floating point value
    in percent) and temperature (as a floating point value in Celsius).
    Unlike the read function, this read_retry function will attempt to read
    multiple times (up to the specified max retries) until a good reading can be
    found. If a good reading cannot be found after the amount of retries, a tuple
    of (None, None) is returned. The delay between retries is by default 2
    seconds, but can be overridden.
'''


class DHT22Driver(object):
    def __init__(self, pin):
        self._logger = logging.getLogger('dht22driver_pin_{}'.format(pin))
        self._logger.info('initializing DHT22Driver')
        self._logger.info('pin: {}'.format(pin))

        self._pin = pin
        try:
            self._gpio = GPIO_TO_PIN_TABLE[self._pin]
        except Exception as ex:
            self._logger.info('got ex: {}'.format(ex))
            self._logger.error('pin {} is not in GPIO table'.format(pin))
            raise ex

        self._temp = None
        self._humidity = None
        self._last_read_time = datetime.min

    def read_sensor_data(self):
        h, t = dht.read_retry(sensor=dht.DHT22, pin=self._gpio, retries=5, delay_seconds=0.5)
        if not self._check_values(h, t):
            return
        self._logger.debug('read dht22, pin: {}, gpio: {}, t: {}, h: {}'.format(self._pin, self._gpio, t, h))
        self._temp = t
        self._humidity = h
        self._last_read_time = datetime.now()

    def _check_values(self, h, t):
        if h is None or t is None:
            return False
        if h > 100 or h < 0 or t < -20 or t > 100:
            self._logger.error(f'readings values seem to be bad, h: {h}, t: {t}')
            return False
        return True

    def get_temp(self):
        if (datetime.now() - self._last_read_time).seconds > cfg.DHT22_MINIMAL_READ_DELTA_SEC:
            self.read_sensor_data()
        return self._temp

    def get_humidity(self):
        if (datetime.now() - self._last_read_time).seconds > cfg.DHT22_MINIMAL_READ_DELTA_SEC:
            self.read_sensor_data()
        return self._humidity

    def get_pin(self):
        return self._pin
