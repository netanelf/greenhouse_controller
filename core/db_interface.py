import threading
from datetime import datetime


class DbInterface(object):
    def __init__(self):
        self._write_lock = threading.RLock()

    def write_sensor_data_to_db(self, sensor_name: str, measurement_time: datetime, value: float):
        raise NotImplemented