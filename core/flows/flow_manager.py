import logging
from typing import List
from .actions import ActionO
from.events import EventO
from .conditions import ConditionO
import threading


class FlowManager(object):
    def __init__(self, flow_name: str, event: EventO, conditions, actions: List[ActionO]):
        self._logger = logging.getLogger(f'{self.__class__.__name__}_{flow_name}')
        self._name = flow_name
        self._event: EventO = event
        self._conditions: List[ConditionO] = conditions
        self._actions: List[ActionO] = actions
        self._action_t = None
        self._logger.info(f'Created Flow: {self._name}, event: {self._event}, conditions: {self._conditions}, actions: {self._actions}')

    def run_flow(self):
        if self._check_event():
            if self._check_conditions():
                self._logger.info('actions should be triggered')
                self._perform_actions()

    def _check_event(self) -> bool:
        return self._event.check_should_fire()

    def _check_conditions(self) -> bool:
        if self._conditions is None:
            return True
        for c in self._conditions:
            if not c.check_condition():
                self._logger.info(f'condition {c} does not satisfy running flow')
                return False
        return True

    def _perform_actions(self):
        # TODO: maybe better to implement with ThreadPoolExecutor, and ensure not to many threads are running/ close nicely etc.
        self._action_t = threading.Thread(target=self._thread_func)
        self._logger.info('starting actions thread')
        self._action_t.start()

    def _thread_func(self):
        for a in self._actions:
            try:
                a.perform_action()
            except Exception as ex:
                self._logger.exception(ex)
        self._logger.info('actions thread ended')

