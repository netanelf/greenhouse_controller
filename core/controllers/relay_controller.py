__author__ = 'netanel'
import logging


class RelayController(object):
    def __init__(self, name, pin, shift_register, state=0):
        self.name = name
        self.pin = pin
        self.sr = shift_register
        self.logger = logging.getLogger(name)

        self.change_state(new_state=state)
        self.state = state

    def change_state(self, new_state):
        if self.check_state(new_state):
            self.sr.change_bit(pin=self.pin, new_state=new_state)
            self.state = new_state
        else:
            self.logger.info('state: {} is not legal'.format(new_state))

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

