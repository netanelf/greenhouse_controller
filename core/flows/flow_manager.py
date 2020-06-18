import logging
from typing import List
from .actions import ActionO
from.events import EventO


class FlowManager(object):
    def __init__(self, flow_name: str, event: EventO, conditions, actions: List[ActionO]):
        self._logger = logging.getLogger(f'{self.__class__.__name__}_{flow_name}')
        self._name = flow_name
        self._event: EventO = event
        self._conditions = conditions
        self._actions: List[ActionO] = actions

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

    def _perform_actions(self):
        for a in self._actions:
            a.perform_action()
