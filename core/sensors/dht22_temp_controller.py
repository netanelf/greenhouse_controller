__author__ = 'netanel'


from sensor_controller import SensorController, Measurement
from django.utils import timezone
import random


class DHT22TempController(SensorController):
    """
    DHT22 temperature & humidity sensor controller
    """
    def __init__(self, name, dht22_driver, simulate=True):
        super(DHT22TempController, self).__init__(name)
        self._dht22_driver = dht22_driver
        self._last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=None)
        self._simulate = simulate

    def read(self):
        super(DHT22TempController, self).read()
        if self._simulate:
            t = self.simulate_data()
        else:
            t = self._dht22_driver.get_temp()
            if t is None:
                self._logger.error('could not read data from sensor: {},'.format(self._name))
                t = 0
        self._last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=t)
        return self._last_read

    def simulate_data(self):
        return random.randint(20, 40)
