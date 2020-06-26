#!/usr/bin/python
# Code sourced from AdaFruit discussion board: https://www.adafruit.com/forums/viewtopic.php?f=8&t=34922

import random
from django.utils import timezone
from .sensor_controller import SensorController, Measurement, history_appender_decorator


class TSL2561LuxController(SensorController):
    def __init__(self, name, address=0x39, debug=False, pause=0.8, simulate=True):
        super(TSL2561LuxController, self).__init__(name)
        self._logger.info('initializing TSL2561LuxController')
        self._logger.info('name: {}'.format(name))
        self._logger.info('address: {}'.format(address))
        self._logger.info('debug: {}'.format(debug))
        self._logger.info('pause: {}'.format(pause))
        self._logger.info('simulate: {}'.format(simulate))

        self.simulate = simulate
        if not self.simulate:
            from core.drivers import Adafruit_TSL2561
            self.address = address
            self.pause = pause
            self.debug = debug
            self.conn = Adafruit_TSL2561.Adafruit_TSL2561(address=address, debug=debug)
            self.conn.begin()

    @history_appender_decorator
    def read(self):
        if self.simulate:
            l = self.simulate_data()
        else:
            l = self.conn.calculate_avg_lux()
            #l = self.read_lux()
            #if l is None:
            #    self._logger.error('could not read data from sensor: {},'.format(self._name))
            #    l = 0
        self._last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=l)
        return self._last_read

    def simulate_data(self):
        return random.randrange(0, 17000)


    '''
    # for CS package
    if (ratio >= 0) and (ratio <= 0.52):
        lux = (0.0315 * ambient) - (0.0593 * ambient * (ratio**1.4))
    elif ratio <= 0.65:
        lux = (0.0229 * ambient) - (0.0291 * IR)
    elif ratio <= 0.80:
        lux = (0.0157 * ambient) - (0.018 * IR)
    elif ratio <= 1.3:
        lux = (0.00338 * ambient) - (0.0026 * IR)
    elif ratio > 1.3:
        lux = 0


    # for T, FN, CL packages
    if (ratio >= 0) and (ratio <= 0.50):
        lux = (0.0304 * ambient) - (0.062 * ambient * (ratio**1.4))
    elif ratio <= 0.61:
        lux = (0.0224 * ambient) - (0.031 * IR)
    elif ratio <= 0.80:
        lux = (0.0128 * ambient) - (0.0153 * IR)
    elif ratio <= 1.3:
        lux = (0.00146 * ambient) - (0.00112 * IR)
    elif ratio > 1.3:
        lux = 0

    if self.debug:
        print "IR Result", IR
        print "Ambient Result", ambient
        print "gain", self.gain
        print "ratio", ratio
        print "lux", lux

    return lux
    '''

