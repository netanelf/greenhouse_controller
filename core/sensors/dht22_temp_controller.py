__author__ = 'netanel'


from sensor_controller import SensorController, Measurement
from django.utils import timezone
from sensor_controller import GPIO_TO_PIN_TABLE
#import Adafruit_DHT as dht
import random
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


class DHT22TempController(SensorController):
    """
    DHT22 temperature & humidity sensor controller
    """
    def __init__(self, name, pin_number, simulate=True):
        super(DHT22TempController, self).__init__(name)
        try:
            self._pin_number = GPIO_TO_PIN_TABLE[pin_number]
        except Exception as ex:
            self._logger.info('got ex: {}'.format(ex))
            self._logger.error('pin {} is not in GPIO table'.format(pin_number))
            raise ex
        self._last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=None)
        self._simulate = simulate

    def read(self):
        super(DHT22TempController, self).read()
        if self._simulate:
            t = self.simulate_data()
        else:
            import Adafruit_DHT as dht
            
            h, t = dht.read_retry(sensor=dht.DHT22, pin=self._pin_number,retries=3, delay_seconds=0.5)
            if t is None:
                self._logger.error('could not read data from sensor: {},'.format(self._name))
                t = 0
        self._last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=t)
        return self._last_read

    def simulate_data(self):
        return random.randint(20, 40)
