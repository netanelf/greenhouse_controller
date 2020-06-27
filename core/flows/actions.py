from core.sensors.sensor_controller import SensorController
from core.controllers.relay_controller import RelayController
from core.db_interface import DbInterface
from django.utils import timezone
import logging
import requests


class ActionO(object):
    def __init__(self, name):
        self._logger = logging.getLogger(f'{self.__class__.__name__}_{name}')
        self._name = name

    def perform_action(self):
        raise NotImplemented

    def get_name(self):
        return self._name


class ActionSaveSensorValToDBO(ActionO):
    def __init__(self, name, sensor: SensorController, db_interface: DbInterface):
        super(ActionSaveSensorValToDBO, self).__init__(name)
        self._sensor_controller = sensor
        self._db_interface = db_interface

    def perform_action(self):
        self._logger.debug('perform action called')
        measurement = self._sensor_controller.get_last_read()
        if (timezone.now() - measurement.time).seconds > 10:
            self._logger.info(f'sensor last data is old ({measurement.time}), initiating a read')
            measurement = self._sensor_controller.read()
        self._db_interface.write_sensor_data_to_history_db(
            sensor_name=measurement.sensor_name,
            measurement_time=measurement.time,
            value=measurement.value)


class ActionSetRelayStateO(ActionO):
    def __init__(self, name, relay: RelayController, state: bool):
        super(ActionSetRelayStateO, self).__init__(name)
        self._relay_controller = relay
        self._wanted_state = state

    def perform_action(self):
        self._logger.debug('perform action called')
        if self._relay_controller.get_state() != self._wanted_state:
            self._relay_controller.change_state(new_state=self._wanted_state)


class ActionSendEmailO(ActionO):
    def __init__(self, name, brain, address: str, subject: str, message: str):
        super(ActionSendEmailO, self).__init__(name)
        self._brain = brain
        self._address = address
        self._subject = subject
        self._message = message

    def perform_action(self):
        self._logger.debug('going to send an email')

        api_key = self._brain._configuration.get('sendgrid_api_key')
        sender_address = self._brain._configuration.get('sendgrid_sender_address')

        if (api_key == None or sender_address == None):
            self._logger.debug('wanted to send an email, but the api key or sender address are not configured!')
            return
       
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        content = {
            'personalizations': [
                {
                    'to': [
                        {
                            'email': self._address
                        }
                    ],
                    'subject': self._subject,
                }
            ],
            'from': {
                'email': sender_address
            },
            'content': [
                {
                    'type': 'text/plain',
                    'value': self._message
                }
            ]
        }
        r = requests.post('https://api.sendgrid.com/v3/mail/send', headers = headers, json = content)
        
        if (r.status_code == 202):
            self._logger.debug('sent the email successfully')
        else:
            self._logger.debug('something went wrong when sending the email, see the following message')
            self._logger.debug(r.text)


