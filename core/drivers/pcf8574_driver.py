__author__ = 'netanel'

import logging
import i2c_driver


class PCF8574Driver(object):
    """
    control a PCF8574 IO expander
    address: I2C address of the chip
    """

    def __init__(self, address, simulate=True):
        self.address = address
        self.size = 8
        self.state = [1] * self.size
        self.simulate = simulate
        self.logger = logging.getLogger('PVF8574Driver')

        if not simulate:
            self.conn = i2c_driver.I2CDevice(addr=self.address)

        self.clear_register()

    def clear_register(self):
        """
        write 0 to all registers
        :return:
        """
        if not self.simulate:
            self.conn.write_cmd(cmd=0xFF)

        self.state = [0] * self.size

    def change_bit(self, pin, new_state):
        """
        change one "bit" in the shift register, keep all other bits untouched
        :param pin: pin/ bit number
        :param new_state: new value
        """


        new_full_state = list(self.state)
        self.logger.debug('old state: {}'.format(new_full_state))
        new_full_state[pin] = new_state
        self.logger.debug('new state: {}'.format(new_full_state))
        new_full_state.reverse()
        new_full_state = [str(bit) for bit in new_full_state]
        b = ''
        for bit in new_full_state:
            b += bit

        decimal_output = int(b, 2)
        self.logger.debug('decimal output: {}'.format(decimal_output))
        if not self.simulate:
            self.conn.write_cmd(decimal_output)

        self.state[pin] = new_state


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    pcf = PCF8574Driver(address=0x80, simulate=True)

    print 'initial state: {}'.format(pcf.state)

    for i in range(5):
        pcf.change_bit(pin=i, new_state=1)

