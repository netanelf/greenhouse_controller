import logging

from core.sensors.sensor_controller import SensorController


class ConditionO(object):
    def __init__(self, name):
        self._logger = logging.getLogger(f'{self.__class__.__name__}_{name}')
        self._name = name

    def check_condition(self) -> bool:
        raise NotImplemented

    def get_name(self):
        return self._name

    def __str__(self):
        return self._name


class ConditionSensorValEqO(ConditionO):
    def __init__(self, name, sensor: SensorController, value: float):
        super(ConditionSensorValEqO, self).__init__(name)
        self._sensor = sensor
        self._value = value
        self._epsilon = 10-6

    def check_condition(self) -> bool:
        if abs(self._sensor.read().value - self._value) < self._epsilon:
            return True
        return False


class ConditionSensorValBiggerO(ConditionO):
    def __init__(self, name, sensor: SensorController, value: float):
        super(ConditionSensorValBiggerO, self).__init__(name)
        self._sensor = sensor
        self._value = value

    def check_condition(self) -> bool:
        if self._sensor.read().value > self._value:
            return True
        return False


class ConditionSensorValSmallerO(ConditionO):
    def __init__(self, name, sensor: SensorController, value: float):
        super(ConditionSensorValSmallerO, self).__init__(name)
        self._sensor = sensor
        self._value = value

    def check_condition(self) -> bool:
        if self._sensor.read().value < self._value:
            return True
        return False
