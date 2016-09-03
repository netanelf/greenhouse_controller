#!/usr/bin/python
# Code sourced from AdaFruit discussion board: https://www.adafruit.com/forums/viewtopic.php?f=8&t=34922

import time
import random
#Adafruit_I2C from https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_I2C/Adafruit_I2C.py

from django.utils import timezone
from sensor_controller import SensorController, Measurement
from core.drivers import Adafruit_TSL2561


class TSL2561LuxController(SensorController):
    def __init__(self, name, address=0x39, debug=False, pause=0.8, simulate=True):
        super(TSL2561LuxController, self).__init__(name)
        self.simulate = simulate
        if not self.simulate:
            #global Adafruit_I2C
            #from Adafruit_I2C import Adafruit_I2C
            #from core.drivers import i2c_driver
            #self.i2c = Adafruit_I2C(address)
            self.address = address
            self.pause = pause
            self.debug = debug
            self.conn = Adafruit_TSL2561(address=address, debug=debug)
            self.conn.begin()
            #self.gain = 0  # no gain preselected
            #self.i2c.write8(0x80, 0x03)     # enable the device

        self.last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=None)

    def read(self):
        super(TSL2561LuxController, self).read()
        if self.simulate:
            l = self.simulate_data()
        else:
            l = self.conn.calculate_avg_lux()
            #l = self.read_lux()
            #if l is None:
            #    self._logger.error('could not read data from sensor: {},'.format(self._name))
            #    l = 0
        self.last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=l)
        return self.last_read

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

