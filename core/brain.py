__author__ = 'netanel'

import logging
from datetime import timedelta
from time import sleep
import threading
import os
import sys
from typing import List, Set

import cfg
from core.utils import init_logging, get_root_path, update_keep_alive, register_keep_alive
from core.db_backup import DbBackupper
from core.failurs_manager import FailureManager
from core.sensors.sensor_controller import Measurement
from core.sensors.dht22_temp_controller import DHT22TempController
from core.sensors.dht22_humidity_controller import DHT22HumidityController
from core.sensors.ds18b20_temp_controller import DS18B20TempController
from core.sensors.tsl2561_lux_controller import TSL2561LuxController
from core.sensors.digital_input_controller import DigitalInputController
from core.sensors.flow_sensor_controller import FlowSensorController
from core.drivers.dht22_driver import DHT22Driver
from core.drivers import sr_driver, dht22_driver, pcf8574_driver
from core.drivers.sht_driver import ShtDriver
from core.sensors.sht_humidity_controller import ShtHumidityController
from core.sensors.sht_temp_controller import ShtTempController
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')
import django
django.setup()
from django.utils import timezone
from django.db.utils import OperationalError
from greenhouse_app.models import *
from greenhouse_app.commands import *
from core.flows.actions import *
from core.flows.events import *
from core.flows.conditions import *
from core.flows.flow_manager import FlowManager
from core.db_interface import DbInterface


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
        self._db_interface = DbInterface()
        self.helper_threads = {}
        self.start_helper_threads()
        self._crate_image_capturing_object()
        self._sr = sr_driver.SRDriver(SER=cfg.SER, RCLK=cfg.RCLK, SRCLK=cfg.SRCLK, ENABLE=cfg.ENABLE,
                                      register_size=cfg.REGISTER_SIZE, simulate=self._simulate_hw)

        self._read_configuration_from_db()

        self._last_read_time = timezone.now()
        self._last_image_take_time = timezone.now()
        self._last_flow_run_time = timezone.now()
        self._last_relay_set_time = timezone.now()
        self._last_keepalive_time = timezone.now()
        self._last_configuration_time = timezone.now()

        self._data = []
        self._killed = False

        register_keep_alive(name=self.__class__.__name__)

        self._logger.info('Brain Finished Init')

    def _read_configuration_from_db(self):
        self._logger.info('reading configurations, sensors relays from db')
        # all sensors
        self._dht_22_drivers: List[DHT22Driver] = []
        self._sht_drivers: List[ShtDriver] = []
        self._sensors: List[SensorController] = []
        self._create_sensor_controllers()

        # all relays
        self._relays: List[RelayController] = []
        self._create_relay_controllers()

        self._controller_objects: List = self._sensors + self._relays
        self._register_sensors_and_relays()

        self._configuration = {}
        self._update_configurations()

        # flows
        self._actions: List[ActionO] = self._populate_actions()
        self._conditions: List[ConditionO] = self._populate_conditions()
        self._flow_managers: List[FlowManager] = []
        self._create_flow_managers()

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

    def _crate_image_capturing_object(self):
        save_path = os.path.join(get_root_path(), 'logs', 'images')
        self._capturer = ImageCapture(
            save_path=save_path,
            failure_manager=self.helper_threads['failure_manager'],
            args_for_raspistill=cfg.RASPISTILL_ARGS,
            simulate=self._simulate_hw)

    def run(self):
        while not self._killed:
            try:
                if timezone.now() - self._last_flow_run_time > timedelta(seconds=cfg.FLOW_MANAGERS_RESOLUTION):
                    self._process_commands()
                    if self._configuration['manual_mode'] == 0:
                        for f in self._flow_managers:
                            f.run_flow()
                    # else:
                    #     self._logger.debug('manual mode ON, avoiding flow run')
                    #     self._run_actions_manually()
                    self._last_flow_run_time = timezone.now()

                if timezone.now() - self._last_read_time > timedelta(seconds=cfg.SENSOR_READING_RESOLUTION):
                    self._logger.info('brain sensors read cycle')
                    self._last_read_time = timezone.now()
                    self._issue_sensors_and_relays_read()
                    self._write_data_to_db()
                    self._logger.info('brain sensors read cycle end')

                if timezone.now() - self._last_image_take_time > timedelta(seconds=cfg.CAMERA_REFRESH_RESOLUTION):
                    self._logger.info('brain image capture cycle')
                    self._last_image_take_time = timezone.now()
                    self._capturer.update_static_image()
                    self._logger.info('brain image capture cycle end')

                if timezone.now() - self._last_keepalive_time > timedelta(seconds=cfg.KEEP_ALIVE_RESOLUTION):
                    self._logger.info('brain keepalive cycle')
                    self._last_keepalive_time = timezone.now()
                    update_keep_alive(name=self.__class__.__name__, failure_manager=self.helper_threads['failure_manager'])
                    self._logger.info('brain keepalive cycle end')

                if timezone.now() - self._last_configuration_time > timedelta(seconds=cfg.CONFIGURATION_RESOLUTION):
                    self._logger.info('brain configuration cycle')
                    self._last_configuration_time = timezone.now()
                    self._update_configurations()
                    self._logger.info('brain configuration cycle end')

            except Exception as ex:
                self._logger.error('in main brain cycle, got exception:')
                self._logger.exception(ex)

            sleep(0.1)
        self._logger.info('brain killed')

    def _create_sensor_controllers(self):
        """
        build controllers for all sensors
        - DHT22 (temp + humidity) sensors
        - DS18B20 (temp) sensors
        - TSL2561 (lux) sensors
        """
        for s in Sensor.objects.order_by():
            self._logger.debug('found sensor: ({}), creating controller'.format(s))

            if isinstance(s, Dht22TempSensor):
                dht_22_driver = self._get_dht22_driver(pin=s.pin)
                self._logger.debug('sensor: ({}) is dht22temp, creating controller'.format(s))
                self._sensors.append(DHT22TempController(name=s.name, dht22_driver=dht_22_driver, simulate=s.simulate))

            elif isinstance(s, Dht22HumiditySensor):
                dht_22_driver = self._get_dht22_driver(pin=s.pin)
                self._logger.debug('sensor: ({}) is dht22humidity, creating controller'.format(s))
                self._sensors.append(DHT22HumidityController(name=s.name, dht22_driver=dht_22_driver, simulate=s.simulate))

            elif isinstance(s, Ds18b20Sensor):
                self._logger.debug('sensor: ({}) is ds18b20, creating controller'.format(s))
                self._sensors.append(DS18B20TempController(name=s.name, device_id=s.device_id, simulate=s.simulate))

            elif isinstance(s, Tsl2561Sensor):
                self._logger.debug('sensor: ({}) is tsl2561, creating controller'.format(s))
                self._sensors.append(TSL2561LuxController(name=s.name, address=int(s.device_id, 16), debug=False, simulate=s.simulate))

            elif isinstance(s, DigitalInputSensor):
                self._logger.debug('sensor: ({}) is digitalInput, creating controller'.format(s))
                self._sensors.append(DigitalInputController(name=s.name, pin=s.pin, simulate=s.simulate))

            elif isinstance(s, FlowSensor):
                self._logger.debug('sensor: ({}) is FlowSensor, creating controller'.format(s))
                self._sensors.append(FlowSensorController(name=s.name, pin=s.pin, simulate=s.simulate, mll_per_pulse=s.mll_per_pulse))

            elif isinstance(s, ShtHumiditySensor):
                sht_driver = self._get_sht_driver(address=int(s.i2c_address, 16))
                self._logger.debug('sensor: ({}) is ShtHumiditySensor, creating controller'.format(s))
                self._sensors.append(ShtHumidityController(name=s.name, sht_driver=sht_driver, simulate=s.simulate))

            elif isinstance(s, ShtTempSensor):
                sht_driver = self._get_sht_driver(address=int(s.i2c_address, 16))
                self._logger.debug('sensor: ({}) is ShtTempSensor, creating controller'.format(s))
                self._sensors.append(ShtTempController(name=s.name, sht_driver=sht_driver, simulate=s.simulate))
            else:
                self._logger.error(f'sensor {s} has no corresponding controller object')

    def _create_relay_controllers(self):
        """
        build controllers for all relays in DB
        """
        self._logger.debug('creating a Shift Register controller to control all relays')

        #self._sr = pcf8574_driver.PCF8574Driver(address=0x20, simulate=self._simulate_hw)
        for r in Relay.objects.order_by():
            self._logger.debug('found relay: ({}), creating controller'.format(r))
            self._relays.append(RelayController(name=r.name, pin=r.pin, shift_register=self._sr, state=int(r.default_state), invert_polarity=r.inverted, simulate=r.simulate))

    def _register_sensors_and_relays(self):
        self._logger.info('registering sensors')
        for c in self._controller_objects:
            self._db_interface.register_sensor(sensor_name=c.get_name())

    def _populate_actions(self):
        action_objects_list = []
        for a in Action.objects.all():
            ao = self._create_action_objects(actions=[a])
            action_objects_list.extend(ao)
        return action_objects_list

    def _populate_conditions(self):
        condition_objects_list = []
        for c in Condition.objects.all():
            co = self._create_condition_object(condition=c)
            condition_objects_list.append(co)
        return condition_objects_list

    def _create_flow_managers(self):
        self._logger.debug('creating flow managers')
        for f in Flow.objects.all():
            self._logger.debug(f'found flow in db: {f.name}')
            event = f.event
            conditions = f.conditions
            actions = f.actions
            wanted_actions_names = [a.name for a in actions.all()]
            wanted_conditions_names = [c.name for c in conditions.all()]
            event_object = self._create_event_object(event)
            actions_objects_list = self._get_actions_from_actions_names(wanted_actions_names)
            conditions_objects_list = self._get_conditions_from_aconditions_names(wanted_conditions_names)
            flow_object = FlowManager(flow_name=f.name,
                                      event=event_object,
                                      conditions=conditions_objects_list,
                                      actions=actions_objects_list)
            self._flow_managers.append(flow_object)

    def _get_actions_from_actions_names(self, actions_names: List[str]) -> List[ActionO]:
        """
        iterate over names to ensure objects are in the order of the name list
        :param actions_names:
        :return:
        """
        actions = []
        for action_name in actions_names:
            for a in self._actions:
                if a.get_name() == action_name:
                    actions.append(a)
        assert len(actions) == len(actions_names)
        return actions

    def _get_conditions_from_aconditions_names(self, conditions_names: List[str]) -> List[ConditionO]:
        conditions = []
        for condition_name in conditions_names:
            for c in self._conditions:
                if c.get_name() == condition_name:
                    conditions.append(c)
        assert len(conditions) == len(conditions_names)
        return conditions

    def _create_event_object(self, event: Event):
        if isinstance(event, EventAtTimeTDays):
            return EventAtTimeTDaysO(name=str(event), t=event.event_time, days=event.event_days)
        elif isinstance(event, EventAtTimeT):
            return EventAtTimeTO(name=str(event), t=event.event_time)
        elif isinstance(event, EventEveryDT):
            return EventEveryDTO(name=str(event), dt=event.event_delta_t)
        else:
            self._logger.error(f'could not find object for event: {event}')

    def _create_condition_object(self, condition: Condition):
        if isinstance(condition, ConditionSensorValEq):
            sensor_name = condition.sensor.name
            sensor = next((x for x in self._controller_objects if x.get_name() == sensor_name), None)
            return ConditionSensorValEqO(name=str(condition),
                                         sensor=sensor,
                                         value=condition.val)
        elif isinstance(condition, ConditionSensorValBigger):
            sensor_name = condition.sensor.name
            sensor = next((x for x in self._controller_objects if x.get_name() == sensor_name), None)
            return ConditionSensorValBiggerO(name=str(condition),
                                             sensor=sensor,
                                             value=condition.val)
        elif isinstance(condition, ConditionSensorValSmaller):
            sensor_name = condition.sensor.name
            sensor = next((x for x in self._controller_objects if x.get_name() == sensor_name), None)
            return ConditionSensorValSmallerO(name=str(condition),
                                              sensor=sensor,
                                              value=condition.val)
        else:
            self._logger.error(f'could not find object for condition: {condition}')

    def _create_action_objects(self, actions):
        action_object_list = []
        for a in actions:
            if isinstance(a, ActionSaveSensorValToDB):
                sensor_name = a.sensor.name
                action_object_list.append(
                    ActionSaveSensorValToDBO(name=str(a),
                                             sensor=next((x for x in self._controller_objects if x.get_name() == sensor_name), None),
                                             db_interface=self._db_interface)
                )
            elif isinstance(a, ActionSetRelayState):
                relay_name = a.relay.name
                relay_obj = next((x for x in self._relays if x.get_name() == relay_name), None)
                action_object_list.append(
                    ActionSetRelayStateO(
                        name=str(a),
                        relay=relay_obj,
                        state=a.state
                    )
                )
            elif isinstance(a, ActionSendEmail):
                action_object_list.append(
                    ActionSendEmailO(
                        name=a.name,
                        brain=self,
                        address=a.address,
                        subject=a.subject,
                        message=a.message
                    )
                )
            elif isinstance(a, ActionCaptureImageAndSave):
                action_object_list.append(
                    ActionCaptureImageAndSaveO(
                        name=a.name,
                        image_capturer=self._capturer,
                        simulate=a.simulate
                    )
                )
            elif isinstance(a, ActionWait):
                action_object_list.append(
                    ActionWaitO(
                        name=a.name,
                        wait_time=a.wait_time
                    )
                )
            else:
                self._logger.error(f'could not find object for action: {a}')
        return action_object_list

    def _issue_sensors_and_relays_read(self):
        self._logger.debug('issuing a read for all sensors and relays')

        for c in self._controller_objects:
            try:
                m = c.read()
                self._data.append(m)
            except Exception as ex:
                self._logger.exception(ex)

    def _get_dht22_driver(self, pin):
        """
        ensure one driver is created for temp + humidity sensor in the same pin
        :param pin:
        :return:
        """
        for d in self._dht_22_drivers:
            if d.get_pin() == pin:
                return d
        d = dht22_driver.DHT22Driver(pin=pin)
        self._dht_22_drivers.append(d)
        return d

    def _get_sht_driver(self, address):
        """
        ensure one driver is created for temp + humidity sensor in the same address
        :param pin:
        :return:
        """
        for d in self._sht_drivers:
            if d.get_address() == address:
                return d
        d = ShtDriver(i2c_address=address)
        self._sht_drivers.append(d)
        return d

    def _write_data_to_db(self):
        self._logger.debug('in _write_data_to_db')
        self._db_interface.update_sensors_value_current_db(self._data)
        self._data.clear()
        self._logger.debug('_write_data_to_db ended')

    def _update_configurations(self):
        """
        read Configuration table from db, set local values to db values
        :return:
        """
        self._logger.debug('in update_configurations')
        for c in Configuration.objects.all():
            self._configuration[c.name] = c.value

    def _run_action_manually(self, action_data):
        self._logger.debug(f'got request to run action: {action_data}')
        action_o = [a for a in self._actions if a.get_name() == action_data.get_name()][0]
        action_o.perform_action()

    def _set_manual_mode(self, data):
        wanted_mode = data.get_on_off()
        if self._configuration['manual_mode'] != wanted_mode:
            self._logger.debug(f'setting manual mode to {wanted_mode}')
            self._configuration['manual_mode'] = wanted_mode
            self._db_interface.write_configuration_int(name='manual_mode', value=wanted_mode)
        else:
            self._logger.debug(f'manual mode is {self._configuration["manual_mode"]}, no need to change to: {wanted_mode}')

    def _process_commands(self):
        commands = Command.objects.all()
        for c in commands:
            timestamp = c.timestamp
            co = get_command_from_json(command_json=c.command_data)
            self._logger.debug(f'got request to execute {co}, timestamp: {timestamp}')

            if (timezone.now() - timestamp) > timedelta(seconds=cfg.SECONDS_AFTER_ALLOW_EVENT_RUN):
                self._logger.error(f'command {co} was requested to run, but timestamp is to old, timestamp: {timestamp}')
                c.delete()
                return

            if isinstance(co, CommandReloadConfiguration):
                self._reload_configuration()
            elif isinstance(co, CommandRunAction):
                self._run_action_manually(action_data=co)
            elif isinstance(co, CommandSetManualMode):
                self._set_manual_mode(data=co)
            elif isinstance(co, CommandSavePicture):
                self._save_picture()
            else:
                self._logger.error(f'{co} not implemented')
            c.delete()

    def _reload_configuration(self):
        self._logger.info('reloading configuration')
        self._read_configuration_from_db()
        self._logger.info('reloaded configuration')

    def _save_picture(self):
        self._logger.info('saving picture')
        self._capturer.capture_image_and_save()

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
            print('running in simulate HW mode')
            b = Brain(simulation_mode=True)
    else:
        print('running in real HW mode')
        b = Brain(simulation_mode=False)
    b.setDaemon(True)
    b.start()

    name = input("Do you want to exit? (Y)")
    print('user entered {}'.format(name))
    if name == 'Y':
        b.kill_brain()
        time.sleep(1)
