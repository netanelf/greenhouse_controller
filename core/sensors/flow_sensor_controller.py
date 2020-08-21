from .sensor_controller import SensorController, Measurement
from random import Random

from threading import Lock
from django.utils import timezone

try:
    import RPi.GPIO as GPIO
except Exception:
    pass


class FlowSensorController(SensorController):
    def __init__(self, name, pin, mll_per_pulse=2, simulate=True):
        super(FlowSensorController, self).__init__(name)
        self._logger.info(f'initializing FlowSensorController')
        self._logger.info(f'name: {name}')
        self._logger.info(f'pin: {pin}')
        self._logger.info(f'simulate: {simulate}')
        self._logger.info(f'mll_per_pulse: {mll_per_pulse}')
        self._pin = pin
        self._mll_per_pulse = mll_per_pulse
        self._simulate = simulate
        self._tic_counter = 0
        self._tic_counter_lock = Lock()

        if self._simulate is True:
            self._randomizer = Random()
        else:
            try:
                GPIO.setmode(GPIO.BOARD)
                GPIO.setup(self._pin, GPIO.IN)
                GPIO.remove_event_detect(self._pin)
                GPIO.add_event_detect(self._pin, GPIO.FALLING, callback=self._sensor_tic_cb)
            except Exception as ex:
                self._logger.exception(ex)

    def _sensor_tic_cb(self, channel):
        if channel == self._pin:
            with self._tic_counter_lock:
                self._tic_counter += 1

    def read(self) -> Measurement:
        if self._simulate:
            self._logger.debug('in simulation mode, random value')
            v = self._randomizer.randint(0, 10)
            self._tic_counter += v

        with self._tic_counter_lock:
            self._last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=self._tic_counter * self._mll_per_pulse)
        return self._last_read
