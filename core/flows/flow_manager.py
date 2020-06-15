from typing import List
from .actions import Action


class FlowManager(object):
    def __init__(self, event, conditions, actions: List[Action]):
        self._event = event
        self._conditions = conditions
        self._actions = actions

    def check_event(self) -> bool:
        raise NotImplemented

    def check_conditions(self) -> bool:
        raise NotImplemented

    def perform_actions(self):
        for a in self._actions:
            a.perform_action()