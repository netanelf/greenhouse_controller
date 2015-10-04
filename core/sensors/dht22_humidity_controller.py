__author__ = 'netanel'


from sensor_controller import SensorController, Measurement
from django.utils import timezone
#import Adafruit_DHT as dht
import random


class DHT22HumidityController(SensorController):
    """
    DHT22 temperature & humidity sensor controller
    """
    def __init__(self, name, pin_number, simulate=True):
        super(DHT22HumidityController, self).__init__(name)
        self._pin_number = pin_number
        self._last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=None)
        self._simulate = simulate

    def read(self):
        super(DHT22HumidityController, self).read()
        if self._simulate:
            h = self.simulate_data()
        else:
            import Adafruit_DHT as dht
            h, t = dht.read_retry(dht.DHT22, self._pin_number)
        self._last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=h)

    def simulate_data(self):
        return random.randint(30,90)
