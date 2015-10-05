__author__ = 'netanel'

import logging


class RelayController(object):
    def __init__(self, name, pin, state=0, simulate=True):
        self._name = name
        self._pin = pin

        self._simulate = simulate
        self._logger = logging.getLogger(name)
        if simulate is False:
            import RPi.GPIO as GPIO
<<<<<<< HEAD
            GPIO.setmode(GPIO.BOARD)
=======
>>>>>>> e6124b162fc53f78a18ac38bc9b991e0272ba21a
            GPIO.setup(self._pin, GPIO.OUT)
        self.change_state(new_state=state)
        self._state = state

    def change_state(self, new_state):
        if self._check_state(new_state):
            if self._simulate:
                self._state = new_state
            else:
                import RPi.GPIO as GPIO
                GPIO.output(self._pin, new_state)
        else:
            self._logger.info('state: {} is not legal'.format(new_state))

    def get_state(self):
        return self._state

    def get_name(self):
        return self._name

    def _check_state(self, state):
        if state in [1, 0]:
            return True
        else:
            return False

    def __unicode__(self):
        return 'name: {}, pin: {}, state: {}'.format(self._name, self._pin, self._state)


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
