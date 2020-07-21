import logging
from datetime import datetime, time, timedelta
import cfg


class EventO(object):
    def __init__(self, name):
        self._logger = logging.getLogger(f'{self.__class__.__name__}_{name}')
        self._name = name

    def check_should_fire(self) -> bool:
        raise NotImplemented


class EventAtTimeTO(EventO):
    def __init__(self, name: str, t: time):
        super().__init__(name)
        self._event_firing_time: time = t
        self._last_firing_time: datetime = datetime.min

    def check_should_fire(self) -> bool:
        now = datetime.now()
        if (now.time() > self._event_firing_time) and \
                (now.time() < (datetime.combine(datetime.today(), self._event_firing_time) + timedelta(seconds=cfg.SECONDS_AFTER_ALLOW_EVENT_RUN)).time()) and \
                (now.date() > self._last_firing_time.date()):
            self._last_firing_time = now
            return True
        return False


class EventEveryDTO(EventO):
    def __init__(self, name, dt: timedelta):
        super().__init__(name)
        self._event_firing_dt = dt
        self._last_event_firing_time = datetime.min

    def check_should_fire(self) -> bool:
        now = datetime.now()
        if now >= self._last_event_firing_time + self._event_firing_dt:
            self._last_event_firing_time = now
            return True
        return False


class EventAtTimeTDaysO(EventAtTimeTO):
    def __init__(self, name: str, t: time, days):
        super().__init__(name, t)
        self._event_days = days

    def check_should_fire(self) -> bool:
        now = datetime.now()
        day_int = now.weekday()
        if str(day_int) in self._event_days and super().check_should_fire():
            return True
        return False

