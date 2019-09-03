__author__ = 'netanel'

import logging
from datetime import timedelta
import time
import threading
import os
import sys

import cfg
import utils
from core.utils import init_logging
from db_backup import DbBackupper
from image_capture import ImageCapture
from failurs_manager import FailureManager
from sensors.sensor_controller import Measurement
from sensors.dht22_temp_controller import DHT22TempController
from sensors.dht22_humidity_controller import DHT22HumidityController
from sensors.ds18b20_temp_controller import DS18B20TempController
from sensors.tsl2561_lux_controller import TSL2561LuxController
from controllers.relay_controller import RelayController
from drivers import sr_driver, dht22_driver, pcf8574_driver
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')
import django
django.setup()
from django.utils import timezone
from django.db.utils import OperationalError
from greenhouse_app.models import Sensor, Measure, Relay, Configuration, ControllerOBject, KeepAlive


class Brain(threading.Thread):
    """
    main control object
     - reads data from sensors
     - controls all output relays
     - makes decisions according to time, sensors, cfg file
    """

    def __init__(self, simulation_mode):
        threading.Thread.__init__(self)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('initializing Brain')
        self._logger.info('simulation_mode: {}'.format(simulation_mode))

        self._simulate_hw = simulation_mode

        # all sensors
        self._dht_22_drivers = []
        self._sensors = []
        self.create_sensor_controllers()

        # all relays
        self._sr = None
        self._relays = []
        self.create_relay_controllers()

        # lcd controller
        if not self._simulate_hw:
            try:
                from drivers import lcd2004_driver
                self.lcd = lcd2004_driver.Lcd()
                self.lcd_alive = 'x'
            except Exception as ex:
                self._logger.exception('could not initialize lcd, ex: {}'.format(ex))

        self._last_read_time = timezone.now()
        self._last_relay_set_time = timezone.now()
        self._last_keepalive_time = timezone.now()
        self._last_configuration_time = timezone.now()
        self._data_lock = threading.RLock()
        self._data = []
        self._killed = False

        # configurations, updated from db
        self._manual_mode = 0

        self.helper_threads = {}
        self.start_helper_threads()
        utils.register_keep_alive(name=self.__class__.__name__)
        self._logger.info('Brain Finished Init')

    def start_helper_threads(self):
        """
        start helper threads: backuper, image_capture etc...
        :return:
        """
        failure_manager = FailureManager()
        failure_manager.setDaemon(True)
        failure_manager.start()
        self.helper_threads['failure_manager'] = failure_manager

        self._logger.info('in start_helper_threads')
        backuper = DbBackupper(failure_manager=self.helper_threads['failure_manager'])
        backuper.setDaemon(True)
        backuper.start()
        self.helper_threads['backuper'] = backuper

        if cfg.CAPTURE_IMAGES:
            save_path = os.path.join(utils.get_root_path(), 'logs', 'images')
            time_between_captures = cfg.IMAGE_FREQUENCY
            capturer = ImageCapture(save_path=save_path,
                                    time_between_captures=time_between_captures,
                                    failure_manager=self.helper_threads['failure_manager'],
                                    args_for_raspistill=['-vf', '-hf'])
            capturer.setDaemon(True)
            capturer.start()
            self.helper_threads['capturer'] = capturer

    def run(self):
        while not self._killed:
            try:
                if timezone.now() - self._last_read_time > timedelta(seconds=cfg.SENSOR_READING_RESOLUTION):
                    self._logger.info('brain sensors read cycle')
                    self._last_read_time = timezone.now()
                    self.issue_sensor_reading()
                    self.write_data_to_db()
                    self._logger.info('brain sensors read cycle end')

                if timezone.now() - self._last_relay_set_time > timedelta(seconds=cfg.RELAY_STATE_WRITING_RESOLUTION):
                    self._logger.info('brain relay set cycle')
                    self._last_relay_set_time = timezone.now()
                    if not self._manual_mode:
                        self.issue_governors_relay_set()
                    self.issue_relay_set()
                    self.write_data_to_db()
                    self._logger.info('brain relay set cycle end')

                if timezone.now() - self._last_keepalive_time > timedelta(seconds=cfg.KEEP_ALIVE_RESOLUTION):
                    self._logger.info('brain keepalive cycle')
                    self._last_keepalive_time = timezone.now()
                    utils.update_keep_alive(name=self.__class__.__name__, failure_manager=self.helper_threads['failure_manager'])
                    self._logger.info('brain keepalive cycle end')

                if timezone.now() - self._last_configuration_time > timedelta(seconds=cfg.CONFIGURATION_RESOLUTION):
                    self._logger.info('brain configuration cycle')
                    self._last_configuration_time = timezone.now()
                    self.update_configurations()
                    self.camera_on_off_set()
                    self.lcd_update()  # TODO: if LCD is actually used - it can have its own update cycle
                    self._logger.info('brain configuration cycle end')

            except Exception as ex:
                self._logger.error('in main brain cycle, got exception:')
                self._logger.exception(ex)

            time.sleep(0.1)
        self._logger.info('brain killed')

    def get_current_data(self):
        with self._data_lock:
            return self._data

    def create_sensor_controllers(self):
        """
        build controllers for all sensors
        - DHT22 (temp + humidity) sensors
        - DS18B20 (temp) sensors
        - TSL2561 (lux) sensors
        """
        for s in Sensor.objects.order_by():
            self._logger.debug('found sensor: ({}), creating controller'.format(s))

            if s.kind.kind == 'dht22temp':
                dht_22_driver = self.get_dht22_controller(pin=s.pin)
                self._logger.debug('sensor: ({}) is dht22temp, creating controller'.format(s))
                self._sensors.append(DHT22TempController(name=s.name, dht22_driver=dht_22_driver, simulate=s.simulate))

            elif s.kind.kind == 'dht22humidity':
                dht_22_driver = self.get_dht22_controller(pin=s.pin)
                self._logger.debug('sensor: ({}) is dht22humidity, creating controller'.format(s))
                self._sensors.append(DHT22HumidityController(name=s.name, dht22_driver=dht_22_driver, simulate=s.simulate))

            elif s.kind.kind == 'ds18b20':
                self._logger.debug('sensor: ({}) is ds18b20, creating controller'.format(s))
                self._sensors.append(DS18B20TempController(name=s.name, device_id=s.device_id, simulate=s.simulate))

            elif s.kind.kind == 'tsl2561':
                self._logger.debug('sensor: ({}) is tsl2561, creating controller'.format(s))
                self._sensors.append(TSL2561LuxController(name=s.name, address=int(s.device_id, 16), debug=False, simulate=s.simulate))

    def create_relay_controllers(self):
        """
        build controllers for all relays in DB
        """
        self._logger.debug('creating a Shift Register controller to control all relays')
        self._sr = sr_driver.SRDriver(SER=cfg.SER, RCLK=cfg.RCLK, SRCLK=cfg.SRCLK, ENABLE=cfg.ENABLE, register_size=cfg.REGISTER_SIZE, simulate=self._simulate_hw)
        #self._sr = pcf8574_driver.PCF8574Driver(address=0x20, simulate=self._simulate_hw)
        for r in Relay.objects.order_by():
            self._logger.debug('found relay: ({}), creating controller'.format(r))
            self._relays.append(RelayController(name=r.name, pin=r.pin, shift_register=self._sr, state=r.state, invert_polarity=r.inverted))

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
        with self._data_lock:
            self._data = []
            for s in self._sensors:
                self._data.append(s.read())

    def lcd_update(self):
        """
        write some data to LCD
        :return:
        """
        if not self._simulate_hw:
            try:
                for i, d in enumerate(self._data):
                    if i < 4:  # write only first four readings
                        name = str(d.sensor_name).replace('humidity', 'H')
                        name = name.replace('temp', 'T')
                        lcd_sensor_string = '{}, {:.1f}'.format(name, d.value)
                        if i == 0:
                            lcd_sensor_string = lcd_sensor_string.ljust(20)
                            if self.lcd_alive == 'x':
                                lcd_sensor_string = lcd_sensor_string[:19] + '+'
                                self.lcd_alive = '+'
                            else:
                                lcd_sensor_string = lcd_sensor_string[:19] + 'x'
                                self.lcd_alive = 'x'
                        self.lcd.lcd_display_string(string=lcd_sensor_string, line=i+1)
            except Exception as ex:
                self._logger.exception('could not write to lcd, ex: {}'.format(ex))
                self.helper_threads['failure_manager'].add_failure(ex=ex, caller=self.__class__.__name__)

    def camera_on_off_set(self):
        """
        update camera state according to lux reading, if below threshold, do not take pictures
        :return:
        """
        self._logger.debug('in camera_on_off_set')
        for sensor_reading in self._data:
            try:
                if 'lux' in sensor_reading.sensor_name:
                    val = sensor_reading.value
                    capturer = self.helper_threads['capturer']
                    if val >= cfg.IMAGE_LUX_THRESHOLD:
                        capturer.change_controller_capture_switch(new_state=True)
                    else:
                        capturer.change_controller_capture_switch(new_state=False)
            except Exception as ex:
                self._logger.exception('in camera_on_off_set, got exception: {}'.format(ex))

    def get_dht22_controller(self, pin):
        """
        ensure one driver is created for temp + humidity sensor in the same pin
        :param pin:
        :return:
        """
        for d in self._dht_22_drivers:
            if d.pin == pin:
                return d
        d = dht22_driver.DHT22Driver(pin=pin)
        self._dht_22_drivers.append(d)
        return d

    def issue_governors_relay_set(self):
        """
        read current governor state and set wanted states for relays according to governor
        """
        for r in Relay.objects.order_by():
            governor = r.time_governor
            if governor is not None:
                self._logger.debug('relay: {}, has governor: {}'.format(r.name, governor))
                governor_state = governor.state

                if governor_state != r.state:
                    self._logger.debug('relay: {}, was changed by governor: {} to state: {}'.format(r.name, governor, governor_state))
                    r.wanted_state = governor_state
                    r.save()

    def issue_relay_set(self):
        """
        read wanted state from DB for every relay, and if different from current state, change.
        """
        for r in Relay.objects.order_by():
            if r.wanted_state != r.state:
                old_state = r.state
                new_state = r.wanted_state
                controller = self.get_relay_by_name(name=r.name)
                try:
                    controller.change_state(new_state=r.wanted_state)
                    self._logger.debug('relay: {} was set to state: {}'.format(controller.get_name(), r.wanted_state))
                    r.state = r.wanted_state
                    r.save()
                    t = timezone.now()
                    m0 = Measurement(sensor_name=r.name, time=t - timedelta(milliseconds=cfg.RELAY_DELTA_MEASURE_MS), value=old_state)
                    self._data.append(m0)
                    m1 = Measurement(sensor_name=r.name, time=t + timedelta(milliseconds=cfg.RELAY_DELTA_MEASURE_MS), value=new_state)
                    self._data.append(m1)

                except Exception as ex:
                    self._logger.exception('some exception: {}'.format(ex))
                    self.helper_threads['failure_manager'].add_failure(ex=ex, caller=self.__class__.__name__)

    def write_data_to_db(self):
        self._logger.debug('in _write_data_to_db')
        with self._data_lock:
            for d in self._data:
                if d is not None:
                    t = 0
                    while t in range(cfg.DB_RETRIES):
                        try:
                            self._logger.debug('looking for controller: {} in Sensors Table'.format(d.sensor_name))
                            controller = ControllerOBject.objects.get(name=d.sensor_name)
                            Measure.objects.create(sensor=controller, measure_time=d.time, val=d.value)
                            break
                        except OperationalError as ex:
                            self._logger.error('while writing to DB got exception, try: {}'.format(t))
                            self._logger.exception(ex)
                            self.helper_threads['failure_manager'].add_failure(ex=ex, caller=self.__class__.__name__)
                            t += 1

    def update_configurations(self):
        """
        read Configuration table from db, set local values to db values
        :return:
        """
        self._logger.debug('in update_configurations')
        for c in Configuration.objects.all():
            if c.name == 'manual_mode':
                self._manual_mode = c.value

    def kill_brain(self):
        self._logger.info('killing helper_threads')
        for thread_name, thread_object in self.helper_threads.items():
            thread_object.stop_thread()

        time.sleep(0.5)
        self._logger.info('killing brain thread')
        self._killed = True


if __name__ == '__main__':
    init_logging(logger_name='greenHouseController', logger_level=cfg.LOG_LEVEL)

    if len(sys.argv) > 1:
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
