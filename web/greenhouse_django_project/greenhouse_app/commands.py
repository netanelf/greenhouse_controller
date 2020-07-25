import json
import logging

_LOGGER = logging.getLogger('commands_logger')


class CommandBase(object):
    def __init__(self, caller: str):
        self._caller = caller


class CommandWithNoData(CommandBase):
    def __init__(self, caller):
        super(CommandWithNoData, self).__init__(caller)


class CommandReloadConfiguration(CommandWithNoData):
    def __init__(self, caller):
        super(CommandReloadConfiguration, self).__init__(caller)

    def serialize(self):
        return json.dumps({'caller': self._caller,
                           'command': 'RELOAD_CONFIGURATION'})


def get_command_from_json(command_json: str):
    o = json.loads(command_json)
    try:
        return COMMANDS_LIST[o['command']](caller=o['caller'])
    except Exception as ex:
        _LOGGER.exception(ex)


COMMANDS_LIST = {
    'RELOAD_CONFIGURATION': CommandReloadConfiguration
}