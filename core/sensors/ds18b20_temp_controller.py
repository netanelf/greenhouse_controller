__author__ = 'netanel'

from .sensor_controller import SensorController, Measurement, history_appender_decorator
from django.utils import timezone
import random
from core.drivers import ds18b20_driver


class DS18B20TempController(SensorController):
    """
    DS18B20 temperature sensor controller
    """
    def __init__(self, name, device_id, simulate=True):
        super(DS18B20TempController, self).__init__(name)
        self._logger.info('initializing DS18B20TempController')
        self._logger.info('name: {}'.format(name))
        self._logger.info('device_id: {}'.format(device_id))
        self._logger.info('simulate: {}'.format(simulate))
        self._device_id = device_id
        self._last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=None)
        self._simulate = simulate

    @history_appender_decorator
    def read(self):
        super(DS18B20TempController, self).read()
        if self._simulate:
            t = self.simulate_data()
        else:
            t = ds18b20_driver.read_ds18b20_temp(sensor_id=self._device_id)
            if t is None:
                self._logger.error('could not read data from sensor: {},'.format(self._name))
                t = 0
        self._last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=t)
        return self._last_read

    def simulate_data(self):
        return random.randint(20, 50)


if __name__ == '__main__':
    from time import sleep
    t_c = DS18B20TempController(name='demo_sensor', device_id='28-031467d282ff', simulate=False)
    for i in range(10):
        print(t_c.read())
        sleep(2)