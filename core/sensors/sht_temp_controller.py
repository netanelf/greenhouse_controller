from .sensor_controller import SensorController, Measurement, history_appender_decorator
from core.drivers.sht_driver import ShtDriver
import random
from django.utils import timezone


class ShtTempController(SensorController):
    def __init__(self, name: str, sht_driver: ShtDriver, simulate: bool = True):
        super(ShtTempController, self).__init__(name)
        self._logger.info('initializing ShtTempController')
        self._logger.info('name: {}'.format(name))
        self._logger.info('sht_driver: {}'.format(sht_driver))
        self._logger.info('simulate: {}'.format(simulate))

        self._sht_driver = sht_driver
        self._simulate = simulate

    def read(self) -> Measurement:
        if self._simulate:
            return Measurement(sensor_name=self._name, time=timezone.now(), value=self._simulate_data())
        else:
            h = self._sht_driver.get_temp()
            if h is None:
                self._logger.error('could not read data from sensor: {},'.format(self._name))

        self._last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=h)
        self._logger.debug('read: {}'.format(self._last_read))
        return self._last_read

    @staticmethod
    def _simulate_data():
        return random.randint(10, 40)
