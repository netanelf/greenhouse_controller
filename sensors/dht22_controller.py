__author__ = 'netanel'


from sensor_controller import SensorController
#import Adafruit_DHT as dht
import random


class DHT22Controller(SensorController):
    """
    DHT22 temperature & humidity sensor controller
    """
    def __init__(self, name, pin_number, simulate=True):
        super(DHT22Controller, self).__init__(name)
        self._pin_number = pin_number
        self._last_read = {name + '_temp': None, name + '_humidity': None}
        self._simulate = simulate

    def read(self):
        super(DHT22Controller, self).read()
        if self._simulate:
            t, h = self.simulate_data()
        else:
            t, h = dht.read_retry(dht.DHT22, self._pin_number)
        self._last_read[self._name + '_temp'] = t
        self._last_read[self._name + '_humidity'] = h
        self._logger.info('read, t: {}, v: {}'.format(self._last_read[self._name + '_temp'],
                                                      self._last_read[self._name + '_humidity']))

    def simulate_data(self):
        return (random.randint(20,40), random.randint(30,90))
