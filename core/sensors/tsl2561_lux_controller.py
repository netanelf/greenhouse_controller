#!/usr/bin/python
# Code sourced from AdaFruit discussion board: https://www.adafruit.com/forums/viewtopic.php?f=8&t=34922

import time
import random
#Adafruit_I2C from https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_I2C/Adafruit_I2C.py
from Adafruit_I2C import Adafruit_I2C
from django.utils import timezone
from sensor_controller import SensorController, Measurement


class TSL2561LuxController(SensorController):
    i2c = None

    def __init__(self, name, address=0x39, debug=False, pause=0.8, simulate=True):
        super(TSL2561LuxController, self).__init__(name)
        self.i2c = Adafruit_I2C(address)
        self.address = address
        self.pause = pause
        self.debug = debug
        self.gain = 0  # no gain preselected
        self.i2c.write8(0x80, 0x03)     # enable the device
        self.simulate = simulate
        self.last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=None)

    def read(self):
        super(TSL2561LuxController, self).read()
        if self.simulate:
            l = self.simulate_data()
        else:
            l = self.read_lux()
            if l is None:
                self._logger.error('could not read data from sensor: {},'.format(self._name))
                l = 0
        self.last_read = Measurement(sensor_name=self._name, time=timezone.now(), value=l)
        return self.last_read

    def simulate_data(self):
        return random.randrange(0, 17000)

    def set_gain(self, gain=1):
        """ Set the gain """
        if gain != self.gain:
            if gain == 1:
                self.i2c.write8(0x81, 0x02)     # set gain = 1X and timing = 402 mSec
                if self.debug:
                    print "Setting low gain"
            else:
                self.i2c.write8(0x81, 0x12)     # set gain = 16X and timing = 402 mSec
                if self.debug:
                    print "Setting high gain"
            self.gain = gain                     # safe gain for calculation
            time.sleep(self.pause)              # pause for integration (self.pause must be bigger than integration time)

    def read_word(self, reg):
        """Reads a word from the I2C device"""
        try:
            wordval = self.i2c.readU16(reg)
            #newval = self.i2c.reverseByteOrder(wordval)
            newval = wordval  # no need to reverse order (at list in raspberry pi)
            if self.debug:
                print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X interperted as 0x%04X" % (self.address, wordval & 0xFFFF, reg, newval & 0xFFFF))
            return newval
        except IOError:
            print("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def read_full(self, reg=0x8C):
        """Reads visible+IR diode from the I2C device"""
        return self.read_word(reg)

    def read_ir(self, reg=0x8E):
        """Reads IR only diode from the I2C device"""
        return self.read_word(reg)

    def read_lux(self, gain=0):
        """Grabs a lux reading either with autoranging (gain=0) or with a specified gain (1, 16)"""
        if gain == 1 or gain == 16:
            self.set_gain(gain)  # low/highGain
            ambient = self.read_full()
            IR = self.read_ir()
        elif gain == 0:  # auto gain
            self.set_gain(16)  # first try highGain
            ambient = self.read_full()
            if ambient < 65535:
                IR = self.read_ir()
            if ambient >= 65535 or IR >= 65535:  # value(s) exeed(s) datarange
                self.set_gain(1)  # set lowGain
                ambient = self.read_full()
                IR = self.read_ir()

        if self.gain == 1:
           ambient *= 16    # scale 1x to 16x
           IR *= 16         # scale 1x to 16x

        ratio = (IR / float(ambient))  # changed to make it run under python 2

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
        '''    
        
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

