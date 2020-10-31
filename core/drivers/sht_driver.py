import logging
from core.drivers.i2c_driver import I2CDevice
import time
from typing import Tuple
from datetime import datetime
import cfg


class ShtDriver(object):
    def __init__(self, i2c_address: int):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._i2c_id = i2c_address
        self._i2c_driver = I2CDevice(addr=self._i2c_id)
        self._temp = None
        self._humidity = None
        self._last_read_time = datetime.min
        self._logger.info('initialized sht')

    def read_data(self) :
        """
        :return: Temperature[C], Humidity[RH]
        """
        self._i2c_driver.write_i2c_block_data(0x2C, [0x06])

        time.sleep(0.1)

        # SHT30 address, 0x44(68)
        # Read data back from 0x00(00), 6 bytes
        # cTemp MSB, cTemp LSB, cTemp CRC, Humididty MSB, Humidity LSB, Humidity CRC
        data = self._i2c_driver.read_i2c_block_data(0x00, 6)

        # Convert the data
        temp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
        humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

        self._temp = temp
        self._humidity = humidity
        self._last_read_time = datetime.now()

    def get_humidity(self) -> float:
        if (datetime.now() - self._last_read_time).seconds > cfg.SHT_MINIMAL_READ_DELTA_SEC:
            self.read_data()
        return self._humidity

    def get_temp(self) -> float:
        if (datetime.now() - self._last_read_time).seconds > cfg.SHT_MINIMAL_READ_DELTA_SEC:
            self.read_data()
        return self._temp

    def get_address(self):
        return self._i2c_id

if __name__ == '__main__':
    logger = logging.getLogger()
    s_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    s_handler.setFormatter(formatter)
    logger.addHandler(s_handler)
    logger.setLevel(logging.DEBUG)

    s = ShtDriver(0x44)
    s.read_data()
    logger.info(f'humidity: {s.get_humidity()}')
    logger.info(f'temp: {s.get_temp()}')

    


