__author__ = 'netanel'

import logging


class RelayController(object):
    def __init__(self, name, pin, state=0, simulate=True):
        self.name = name
        self.pin = pin

        self.simulate = simulate
        self.logger = logging.getLogger(name)
        if simulate is False:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.pin, GPIO.OUT)

        self.change_state(new_state=state)
        self.state = state

    def change_state(self, new_state):
        if self.check_state(new_state):
            if self.simulate:
                self.state = new_state
            else:
                import RPi.GPIO as GPIO
                GPIO.output(self.pin, new_state)
        else:
            self.logger.info('state: {} is not legal'.format(new_state))

    def get_state(self):
        return self.state

    def get_name(self):
        return self.name

    def check_state(self, state):
        if state in [1, 0]:
            return True
        else:
            return False

    def __unicode__(self):
        return 'name: {}, pin: {}, state: {}'.format(self.name, self.pin, self.state)


if __name__ == '__main__':
    r = RelayController(name='demo', pin=8, state=0, simulate=False)
    import time
    for i in range(10):
        print 'setting pin 8 to HIGH'
        r.change_state(new_state=1)
        time.sleep(5)
        print 'setting pin 8 to LOW'
        r.change_state(new_state=0)
        time.sleep(5)
