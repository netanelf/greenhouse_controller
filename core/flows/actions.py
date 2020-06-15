from core.sensors.sensor_controller import SensorController
from core.db_interface import DbInterface
import logging


class Action(object):
    def __init__(self, name):
        self._logger = logging.getLogger(name)
        self._name = name

    def perform_action(self):
        raise NotImplemented


class ActionSaveSensorValToDB(Action):
    def __init__(self, name, sensor: SensorController, db_interface: DbInterface):
        super(ActionSaveSensorValToDB, self).__init__(name)
        self._sensor_controller = sensor
        self._db_interface = db_interface

    def perform_action(self):
        self._logger.debug('perform action called')
        measurement = self._sensor_controller.get_last_read()
        self._db_interface.write_sensor_data_to_db(sensor_name=measurement.sensor_name,
                                                   measurement_time=measurement.time,
                                                   value=measurement.value)
