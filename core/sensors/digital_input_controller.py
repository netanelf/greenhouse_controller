from .sensor_controller import SensorController, Measurement
from random import Random

from django.utils import timezone


class DigitalInputController(SensorController):

    def __init__(self, name, pin, simulate=True):
        super(DigitalInputController, self).__init__(name)
        self._logger.info('initializing DigitalInputSensor')
        self._logger.info('name: {}'.format(name))
        self._logger.info('pin: {}'.format(pin))
        self._logger.info('simulate: {}'.format(simulate))

        self._pin = pin
        self._simulate = simulate

        if self._simulate is True:
            self._randomizer = Random()
        else:
            global GPIO
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read(self) -> Measurement:
        if self._simulate:
            self._logger.debug('in simulation mode, random value')
            v = self._randomizer.randint(0, 1)
        else:
            v = GPIO.input(self._pin)

        self._last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=v)
        return self._last_read

