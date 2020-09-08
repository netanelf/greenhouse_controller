# taken from: https://arduinogeek.wordpress.com/2014/04/23/raspberry-pi-with-i2c-2004-lcd/
try:
    import smbus
except Exception:
    print('could not import smbus')

import logging
from time import sleep
from typing import List


class I2CDevice:
    def __init__(self, addr, port=1):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.addr = addr
        try:
            self.bus = smbus.SMBus(port)
        except Exception as ex:
            print('could not open SMBus')

    # Write a single command
    def write_cmd(self, cmd):
        self.bus.write_byte(self.addr, cmd)
        sleep(0.0001)

    # Write a command and argument
    def write_cmd_arg(self, cmd, data):
        self.bus.write_byte_data(self.addr, cmd, data)
        sleep(0.0001)

    # Write a block of data
    def write_block_data(self, cmd, data):
        self.bus.write_block_data(self.addr, cmd, data)
        sleep(0.0001)

    # Read a single byte
    def read(self):
        return self.bus.read_byte(self.addr)

    # Read
    def read_data(self, cmd):
        return self.bus.read_byte_data(self.addr, cmd)

    # Read a block of data
    def read_block_data(self, cmd):
        return self.bus.read_block_data(self.addr, cmd)

    def write_i2c_block_data(cmd: int, data: List[int]):
        self._logger.info('in write_i2c_block_data')
        bus.write_i2c_block_data(self.addr, cmd, data)

    def read_i2c_block_data(reg: int, len: int):
        self._logger.info('in read_i2c_block_data')
        return(bus.read_i2c_block_data(self.addr, reg, len))


