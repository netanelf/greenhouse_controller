__author__ = 'netanel'


from sensor_controller import SensorController
import Adafruit_DHT as dht
from datetime import datetime


class DHT22Controller(SensorController):
    """
    DHT22 temperature & humidity sensor controller
    """
    def __init__(self, name, pin_number):
        super(DHT22Controller, self).__init__(name, logger)
        self._pin_number = pin_number

    def read(self):
        super(DHT22Controller, self).read()
        t = datetime.now()
        self._last_read = (t, dht.read_retry(dht.DHT22, self._pin_number))
        self._logger('read, t: {}, v: {}'.format(self._last_read[0], self._last_read[1]))


