from core.sensors.sensor_controller import SensorController
from core.db_interface import DbInterface
from django.utils import timezone
import logging


class ActionO(object):
    def __init__(self, name):
        self._logger = logging.getLogger(f'{self.__class__.__name__}_{name}')
        self._name = name

    def perform_action(self):
        raise NotImplemented


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
