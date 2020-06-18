import logging
from datetime import datetime, time, timedelta


class EventO(object):
    def __init__(self, name):
        self._logger = logging.getLogger(f'{self.__class__.__name__}_{name}')
        self._name = name

    def check_should_fire(self) -> bool:
        raise NotImplemented


class EventAtTimeTO(EventO):
    def __init__(self, name: str, t: time):
        super(EventAtTimeTO, self).__init__(name)
        self._event_firing_time: time = t
        self._last_firing_time: datetime = datetime.min

    def check_should_fire(self) -> bool:
        now = datetime.now()
        if now.time() > self._event_firing_time and (now - self._last_firing_time) > timedelta(hours=11):
            self._last_firing_time = now
            return True
        return False
