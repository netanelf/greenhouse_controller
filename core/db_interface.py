import threading
import logging
from datetime import datetime
from cfg import DB_RETRIES

from greenhouse_app.models import ControllerObject, HistoryValue, CurrentValue
from django.db.utils import OperationalError


class DbInterface(object):
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._write_lock = threading.RLock()

    def write_sensor_data_to_history_db(self, sensor_name: str, measurement_time: datetime, value: float):
        with self._write_lock:
            t = 0
            while t in range(DB_RETRIES):
                try:
                    self._logger.debug('looking for controller: {} in Sensors Table'.format(sensor_name))
                    controller = ControllerObject.objects.get(name=sensor_name)
                    HistoryValue.objects.create(sensor=controller, measure_time=measurement_time, val=value)
                    self._logger.debug('wrote data to db')
                    break
                except OperationalError as ex:
                    self._logger.error('while writing to DB got exception, try: {}'.format(t))
                    self._logger.exception(ex)
                    t += 1

    def update_sensors_value_current_db(self, data):
        with self._write_lock:
            for d in data:
                if d is not None:
                    t = 0
                    while t in range(DB_RETRIES):
                        try:
                            controller = ControllerObject.objects.get(name=d.sensor_name)
                            cv = CurrentValue.objects.get(sensor=controller)
                            cv.measure_time = d.time
                            cv.val = d.value
                            cv.save()
                            break
                        except OperationalError as ex:
                            self._logger.error('while writing to DB got exception, try: {}'.format(t))
                            self._logger.exception(ex)
                            t += 1

    def register_sensor(self, sensor_name: str):
        with self._write_lock:
            try:
                controller = ControllerObject.objects.get(name=sensor_name)
                CurrentValue.objects.get_or_create(sensor=controller, measure_time=datetime(2000,1,1,0,0,0), val=0)
            except Exception as ex:
                self._logger.exception(ex)

