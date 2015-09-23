__author__ = 'netanel'

import cfg
import logging
from datetime import datetime, timedelta
from sensors.dht22_controller import DHT22Controller
import csv
import time


class Brain(object):
    """
    main control object
     - reads data from sensors
     - controls all output relays
     - makes decisions according to time, sensors, cfg file
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._sensors = []
        self._create_sensor_controllers()
        self._last_read_time = datetime.now()
        self._reading_issue_time = datetime.now()
        self._data = []
        self._csv_writer = self.initialise_csv()

    def run(self):
        while True:
            if datetime.now() - self._last_read_time > timedelta(seconds=cfg.READING_RESOLUTION):
                self._reading_issue_time = self._last_read_time = datetime.now()
                self.issue_sensor_reading()

                time.sleep(cfg.READING_TIME)
                self.issue_data_gathering()
                self._write_data_to_csv()
                # do many things

            time.sleep(1)

    def _create_sensor_controllers(self):
        """
        build controllers for all sensors
        - DHT22_SENSORS
        - add more later
        """
        for s in cfg.DHT22_SENSORS:
            self._logger.debug('found sensor: ({}, {}), creating controller'.format(s['name'], s['pin']))
            if self._validate_sensor_data(name=s['name']):
                self._sensors.append(DHT22Controller(name=s['name'], pin_number=s['pin']))

    def _validate_sensor_data(self, name):
        """
        ensure all sensors have valid names, pins etc..
        more tests should be added here
        :param name:
        :return: True if parameters are valid, False if not
        """
        for s in self._sensors:
            if s.get_name() == name:
                self._logger.error('name: {} is taken, sensor not added'.format(name))
                return False
        return True

    def issue_sensor_reading(self):
        self._logger.debug('issuing a read for all sensors')
        for s in self._sensors:
            s.read()

    def issue_data_gathering(self):
        self._logger.debug('issuing a data gather for all sensors')
        self._data = []
        for s in self._sensors:
            self._data.append(s.get_read())

    def _write_data_to_csv(self):
        self._logger.debug('in _write_data_to_csv')
        csv_outpud_dictionary = dict()
        csv_outpud_dictionary['time'] = datetime.now()
        for d in self._data:
            csv_outpud_dictionary.update(d)

        self._logger.debug('writing line: {}'.format(csv_outpud_dictionary))
        self._csv_writer.writerow(csv_outpud_dictionary)

    def initialise_csv(self):
        self._logger.info('opening .csv file')
        f = open(name='logs/data_{}.csv'.format(datetime.now()), mode='wb', buffering=1)
        sensor_names = [s.get_read().keys() for s in self._sensors]
        fieldnames = ['time']
        [fieldnames.extend(n) for n in sensor_names]
        self._logger.info('writing to .csv file headers: {}'.format(fieldnames))
        csv_writer = csv.DictWriter(f=f, fieldnames=fieldnames)
        csv_writer.writeheader()
        return csv_writer


def init_logging():
    logger = logging.getLogger()
    s_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(filename='logs/greenHouseCntrl_{}.log'.format(datetime.now().strftime('%d-%m-%y_%H:%M:%S.%f')))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    s_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)
    logger.addHandler(s_handler)
    logger.addHandler(f_handler)
    logger.setLevel(cfg.LOG_LEVEL)


if __name__ == '__main__':
    init_logging()
    b = Brain()
    b.run()

