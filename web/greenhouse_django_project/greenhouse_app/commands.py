import json
import logging
from abc import ABC, abstractmethod
from typing import Dict
_LOGGER = logging.getLogger('commands_logger')


class CommandBase(object):
    def __init__(self, caller: str):
        self._caller = caller

    @abstractmethod
    def serialize(self):
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, obj_json: Dict):
        pass


class CommandWithNoData(CommandBase, ABC):
    def __init__(self, caller):
        super(CommandWithNoData, self).__init__(caller)


class CommandWithData(CommandBase, ABC):
    def __init__(self, caller):
        super(CommandWithData, self).__init__(caller)


class CommandReloadConfiguration(CommandWithNoData):
    def __init__(self, caller):
        super(CommandReloadConfiguration, self).__init__(caller)

    def serialize(self):
        return json.dumps({'caller': self._caller,
                           'command': 'RELOAD_CONFIGURATION'})

    @classmethod
    def deserialize(cls, obj_json: Dict):
        return CommandReloadConfiguration(caller=obj_json['caller'])


class CommandSavePicture(CommandWithNoData):
    def __init__(self, caller):
        super(CommandSavePicture, self).__init__(caller)

    def serialize(self):
        return json.dumps({'caller': self._caller,
                           'command': 'SAVE_PICTURE'})

    @classmethod
    def deserialize(cls, obj_json: Dict):
        return CommandSavePicture(caller=obj_json['caller'])


class CommandRunAction(CommandWithData):
    def __init__(self, caller, action_name):
        super(CommandRunAction, self).__init__(caller)
        self._action_name = action_name

    def get_name(self):
        return self._action_name

    def serialize(self):
        return json.dumps({'caller': self._caller,
                           'command': 'RUN_CATION',
                           'action_name': self._action_name})

    @classmethod
    def deserialize(cls, obj_json: Dict):
        return CommandRunAction(caller=obj_json['caller'], action_name=obj_json['action_name'])


class CommandSetManualMode(CommandWithData):
    def __init__(self, caller, on_off):
        super(CommandSetManualMode, self).__init__(caller)
        self._on_off = on_off

    def get_on_off(self):
        return self._on_off

    def serialize(self):
        return json.dumps({'caller': self._caller,
                           'command': 'SET_MANUAL_MODE',
                           'on_off': self._on_off})

    @classmethod
    def deserialize(cls, obj_json: Dict):
        return CommandSetManualMode(caller=obj_json['caller'], on_off=obj_json['on_off'])


def get_command_from_json(command_json: str):
    o = json.loads(command_json)
    try:
        cmd_class = COMMANDS_LIST[o['command']]
        return cmd_class.deserialize(obj_json=o)

    except Exception as ex:
        _LOGGER.exception(ex)


COMMANDS_LIST = {
    'RELOAD_CONFIGURATION': CommandReloadConfiguration,
    'RUN_CATION': CommandRunAction,
    'SET_MANUAL_MODE': CommandSetManualMode,
    'SAVE_PICTURE': CommandSavePicture
}