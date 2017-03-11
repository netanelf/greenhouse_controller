__author__ = 'netanel'
import logging
from core.sensors.sensor_controller import GPIO_TO_PIN_TABLE

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
        self.logger = logging.getLogger('dht22driver_pin_{}'.format(pin))
        self.logger.info('initializing DHT22Driver')
        self.logger.info('pin: {}'.format(pin))

        self.pin = pin
        try:
            self.gpio = GPIO_TO_PIN_TABLE[self.pin]
        except Exception as ex:
            self.logger.info('got ex: {}'.format(ex))
            self.logger.error('pin {} is not in GPIO table'.format(pin))
            raise ex

        self.temp = None
        self.humidity = None

    def read_sensor_data(self):
        import Adafruit_DHT as dht
        h, t = dht.read_retry(sensor=dht.DHT22, pin=self.gpio, retries=5, delay_seconds=0.5)
        self.logger.debug('read dht22, pin: {}, gpio: {}, t: {}, h: {}'.format(self.pin, self.gpio, t, h))
        self.temp = t
        self.humidity = h

    def get_temp(self):
        if self.temp is None:
            self.read_sensor_data()
        t = self.temp
        self.temp = None
        return t

    def get_humidity(self):
        if self.humidity is None:
            self.read_sensor_data()
        h = self.humidity
        self.humidity = None
        return h
