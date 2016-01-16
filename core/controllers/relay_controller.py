__author__ = 'netanel'
import logging


class RelayController(object):
    def __init__(self, name, pin, shift_register, state=0, simulate=True):
        """
        controll one relay through a shift register
        :param name:
        :param pin: pin on shift register (0-8)
        :param shift_register: shift register controller object
        :param state: initial state
        :return:
        """
        self.name = name
        self.pin = pin
        self.simulate = simulate

        if not self.simulate:
            global GPIO
            import RPi.GPIO as GPIO

        if shift_register is not None:
            self.sr = shift_register
            self.direct = False
        else:
            self.direct = True  # relay is controlled straight from the GPIO
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, state)

        self.logger = logging.getLogger(name)

        self.change_state(new_state=state)
        self.state = state

    def change_state(self, new_state):
        try:
            self.logger.debug('relay: {}, old state: {}, new state: {}'.format(self.name, self.state, new_state))
        except Exception:
            pass
        if self.check_state(new_state):
            if not self.direct:
                self.sr.change_bit(pin=self.pin, new_state=new_state)
            else:
                self.direct_change(new_state)
            self.state = new_state
        else:
            self.logger.info('state: {} is not legal'.format(new_state))

    def direct_change(self, new_state):
        if not self.simulate:
            if new_state == 1:
                GPIO.output(self.pin, 1)
            else:
                GPIO.output(self.pin, 0)
        else:
            pass

    def get_state(self):
        return self.state

    def get_name(self):
        return self.name

    @staticmethod
    def check_state(state):
        if state in [1, 0]:
            return True
        else:
            return False

    def __unicode__(self):
        return 'name: {}, pin: {}, state: {}'.format(self.name, self.pin, self.state)

