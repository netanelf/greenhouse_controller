__author__ = 'netanel'
import time
import logging


class SRDriver(object):
    """
    control a SN74HC595 Shift register
    OE - output enable, enabled in init  TODO: add support for disabling output?
    SRCLR - clear shifty register, not used, ***hold at VCC***
    SRCLK - clock the shift register (input = SER), on LOW to HIGH transition
    RCLK - load all registers into buffer, on LOW to HIGH transition
    SER - data that will go into first register
    """

    def __init__(self, SER, RCLK, SRCLK, ENABLE, register_size=8, simulate=True):
        self.logger = logging.getLogger('SRDriver')

        self.logger.info('initializing SRDriver')
        self.logger.info('SER: {}'.format(SER))
        self.logger.info('RCLK: {}'.format(RCLK))
        self.logger.info('SRCLK: {}'.format(SRCLK))
        self.logger.info('ENABLE: {}'.format(ENABLE))
        self.logger.info('register_size: {}'.format(register_size))
        self.logger.info('simulate: {}'.format(simulate))

        self.ser = SER
        self.rclk = RCLK
        self.srclk = SRCLK
        self.enable = ENABLE
        self.size = register_size
        self.state = [1] * self.size
        self.simulate = simulate

        if not simulate:
            print('not simulate ****************************')
            global GPIO
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.ser, GPIO.OUT)
            GPIO.setup(self.rclk, GPIO.OUT)
            GPIO.setup(self.srclk, GPIO.OUT)
            GPIO.setup(self.enable, GPIO.OUT)

            GPIO.output(self.ser, 0)
            GPIO.output(self.rclk, 0)
            GPIO.output(self.srclk, 0)
            GPIO.output(self.enable, 0)

        self.clear_register()

    def clear_register(self):
        """
        write 0 to all registers
        :return:
        """
        for i in range(self.size):
            self.shift_data(0)

        self.load_output()
        self.state = [0] * self.size

    def shift_data(self, data):
        """
        shift data into register, data should be 0, 1
        :param data:
        :return:
        """
        if self.simulate:
            return
        else:
            if data == 1:
                GPIO.output(self.ser, 1)
            else:
                GPIO.output(self.ser, 0)
            GPIO.output(self.srclk, 1)
            GPIO.output(self.srclk, 0)
            # return ser to 0, if the clocks togle, 0 will be inserted
            GPIO.output(self.ser, 0)

    def load_output(self):
        """
        load shift register data into output latches
        :return:
        """
        if self.simulate:
            return
        else:
            GPIO.output(self.rclk, 1)
            GPIO.output(self.rclk, 0)

    def change_bit(self, pin, new_state):
        """
        change one "bit" in the shift register, keep all other bits untouched
        :param pin: pin/ bit number
        :param new_state: new value
        """
        if not self.simulate:
            self.logger.debug('pin: {}, new_state: {}'.format(pin, new_state))
            new_state = int(new_state)
            new_full_state = list(self.state)
            self.logger.debug('old_SR_state: {}'.format(new_full_state))
            new_full_state[pin] = new_state
            self.logger.debug('new_SR_state: {}'.format(new_full_state))
            new_full_state.reverse()
            for i in new_full_state:
                self.shift_data(i)
            self.load_output()

        self.state[pin] = new_state


if __name__ == '__main__':
    sr = SRDriver(SER=12, RCLK=13, SRCLK=15, ENABLE=11, register_size=8, simulate=False)
    #for i in range(10):
    sr.clear_register()
    for i in range(8):
        sr.change_bit(pin=i, new_state=1)
        time.sleep(10)

