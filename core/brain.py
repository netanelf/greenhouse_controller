__author__ = 'netanel'

import logging
from datetime import timedelta
import time
import threading
import os, sys

import cfg
import utils
from sensors.dht22_temp_controller import DHT22TempController
from sensors.dht22_humidity_controller import DHT22HumidityController
from controllers.relay_controller import RelayController
from drivers import sr_driver
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')
import django
django.setup()
from django.utils import timezone
from greenhouse_app.models import Sensor, Measure, Relay, Configurations


class Brain(threading.Thread):
    """
    main control object
     - reads data from sensors
     - controls all output relays
     - makes decisions according to time, sensors, cfg file
    """

    def __init__(self, simulation_mode):
        threading.Thread.__init__(self)
        self._logger = logging.getLogger(__name__)
        self._simulate_hw = simulation_mode

        # all sensors
        self._sensors = []
        self.create_sensor_controllers()

        # all relays
        self._sr = None
        self._relays = []
        self.create_relay_controllers()

        # lcd controller
        if not self._simulate_hw:
            from drivers import lcd2004_driver
            self.lcd = lcd2004_driver.Lcd()

        self._last_read_time = timezone.now()
        self._reading_issue_time = timezone.now()
        self._data_lock = threading.RLock()
        self._data = []
        self._killed = False

        # configurations, updated from db
        self._manual_mode = 0

    def run(self):
        while not self._killed:
            if timezone.now() - self._last_read_time > timedelta(seconds=cfg.READING_RESOLUTION):
                self.update_configurations()
                self._reading_issue_time = self._last_read_time = timezone.now()
                self.issue_sensor_reading()

                time.sleep(cfg.READING_TIME)
                self.issue_data_gathering()
                self.write_data_to_db()
                if not self._manual_mode:
                    self.issue_governors_relay_set()
                self.issue_relay_set()
                # do many things

            time.sleep(1)
        self._logger.info('brain killed')

    def get_current_data(self):
        with self._data_lock:
            return self._data

    def create_sensor_controllers(self):
        """
        build controllers for all sensors
        - DHT22_SENSORS
        - add more later
        """
        #for s in cfg.DHT22_SENSORS:
        for s in Sensor.objects.order_by():
            self._logger.debug('found sensor: ({}), creating controller'.format(s))

            if s.kind.kind == 'dht22temp':
                self._logger.debug('sensor: ({}) is dht22temp, creating controller'.format(s))
                self._sensors.append(DHT22TempController(name=s.name, pin_number=s.pin, simulate=s.simulate))

            elif s.kind.kind == 'dht22humidity':
                self._logger.debug('sensor: ({}) is dht22humidity, creating controller'.format(s))
                self._sensors.append(DHT22HumidityController(name=s.name, pin_number=s.pin, simulate=s.simulate))

    def create_relay_controllers(self):
        """
        build controllers for all relays in DB
        """
        self._logger.debug('creating a Shift Register controller to control all relays')
        self._sr = sr_driver.SRDriver(SER=40, RCLK=38, SRCLK=36, register_size=8, simulate=True)
        for r in Relay.objects.order_by():
            self._logger.debug('found relay: ({}), creating controller'.format(r))
            self._relays.append(RelayController(name=r.name, pin=r.pin, shift_register=self._sr, state=r.state))

    def get_relay_by_name(self, name):
        """
        find the relay controller object for the given name
        :param name: wanted relay
        :return: controller object
        """
        for r in self._relays:
            if r.get_name() == name:
                return r
        logging.info('searched for relay named: {}, not found'.format(name))
        return False

    def issue_sensor_reading(self):
        self._logger.debug('issuing a read for all sensors')
        for s in self._sensors:
            s.read()

    def issue_data_gathering(self):
        self._logger.debug('issuing a data gather for all sensors')
        with self._data_lock:
            self._data = []
            for s in self._sensors:
                self._data.append(s.get_read())

    def issue_governors_relay_set(self):
        """
        read current governor state and set states for relays according to governor
        """
        for r in Relay.objects.order_by():
            governor = r.time_governor
            if governor is not None:
                self._logger.debug('relay: {}, has governor: {}'.format(r.name, governor))
                governer_state = governor.state

                if governer_state != r.state:
                    self._logger.debug('relay: {}, was changed by governor: {} to state: {}'.format(r.name, governor, governer_state))
                    r.wanted_state = governer_state
                    r.save()

    def issue_relay_set(self):
        """
        read wanted state from DB for every relay, and if different from current state, change.
        """
        for r in Relay.objects.order_by():
            if r.wanted_state != r.state:
                controller = self.get_relay_by_name(name=r.name)
                try:
                    controller.change_state(new_state=r.wanted_state)
                    self._logger.debug('relay: {} was set to state: {}'.format(controller.get_name(), r.wanted_state))
                    r.state = r.wanted_state
                    r.save()
                except Exception as ex:
                    self._logger.info('some exception: {}'.format(ex))

    def write_data_to_db(self):
        self._logger.debug('in _write_data_to_db')
        with self._data_lock:
            for d in self._data:
                self._logger.debug('looking for sensor: {} in Sensors Table'.format(d.sensor_name))
                sensor = Sensor.objects.get(name=d.sensor_name)
                Measure.objects.create(sensor=sensor, time=d.time, val=d.value)

    def update_configurations(self):
        """
        read Configuration table from db, set local values to db values
        :return:
        """
        self._logger.debug('in update_configurations')
        for c in Configurations.objects.all():
            if c.name == 'manual_mode':
                self._manual_mode = c.value

    def kill_brain(self):
        self._logger.info('killing brain thread')
        self._killed = True


def init_logging():
    logger = logging.getLogger()
    s_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(filename=os.path.join(utils.get_root_path(), 'logs', 'greenHouseCntrl_{}.log'
        .format(timezone.make_naive(value=timezone.now(), timezone=timezone.get_current_timezone()).strftime('%d-%m-%y_%H-%M-%S'))))

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    s_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)
    logger.addHandler(s_handler)
    logger.addHandler(f_handler)
    logger.setLevel(cfg.LOG_LEVEL)


if __name__ == '__main__':
    init_logging()
    if str(sys.argv[1]) == 'simulate':
        print 'running in simulate HW mode'
        b = Brain(simulation_mode=True)
    else:
        print 'running in real HW mode'
        b = Brain(simulation_mode=False)
    b.setDaemon(True)
    b.start()

    name = raw_input("Do you want to exit? (Y)")
    print 'user entered {}'.format(name)
    if name == 'Y':
        b.kill_brain()
        time.sleep(1)
