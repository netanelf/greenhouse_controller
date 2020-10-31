from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
from polymorphic.models import PolymorphicModel
from multiselectfield import MultiSelectField
import time
import logging
from enum import Enum


class Units(Enum):
    NA = 'NA'
    Temp = 'C'
    Percent = '%'
    Flow = 'mL/H'
    LiquidVolume = 'mL'
    Bool = 'Bool'
    Luminance = 'Lux'
    Acidity = 'Ph'


class ControllerObject(PolymorphicModel):
    """
    represent a controller object ie. sensor or relay
    this way we can connect a measure to a relay or a sensor
    """
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name


class Sensor(ControllerObject):
    """
    represent one sensor
    """
    simulate = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Dht22TempSensor(Sensor):
    pin = models.PositiveSmallIntegerField()

    def get_unit(self):
        return Units.Temp
    unit = property(get_unit)


class Dht22HumiditySensor(Sensor):
    pin = models.PositiveSmallIntegerField()

    def get_unit(self):
        return Units.Percent
    unit = property(get_unit)


class Ds18b20Sensor(Sensor):
    device_id = models.CharField(max_length=32, default='', help_text='Sensor unique ID')

    def get_unit(self):
        return Units.Temp
    unit = property(get_unit)


class Tsl2561Sensor(Sensor):
    device_id = models.CharField(max_length=32, default='', help_text='I2C address')

    def get_unit(self):
        return Units.Luminance
    unit = property(get_unit)


class DigitalInputSensor(Sensor):
    pin = models.PositiveSmallIntegerField()

    def get_unit(self):
        return Units.Bool
    unit = property(get_unit)


class FlowSensor(Sensor):
    pin = models.PositiveSmallIntegerField()
    mll_per_pulse = models.IntegerField(help_text='[mL] fluid per 1 edge of sensor')

    def get_unit(self):
        return Units.LiquidVolume
    unit = property(get_unit)


class ShtHumiditySensor(Sensor):
    i2c_address = models.CharField(max_length=32, default='', help_text='I2C address')

    def get_unit(self):
        return Units.Percent
    unit = property(get_unit)


class ShtTempSensor(Sensor):
    i2c_address = models.CharField(max_length=32, default='', help_text='I2C address')

    def get_unit(self):
        return Units.Temp
    unit = property(get_unit)


class CurrentValue(models.Model):
    """
    represent one value measurement
    """
    sensor = models.OneToOneField(ControllerObject, on_delete=models.CASCADE)
    measure_time = models.DateTimeField()
    val = models.FloatField()

    def calculate_ts(self):
        t_python = self.measure_time
        t_python = timezone.make_naive(t_python, timezone=timezone.get_current_timezone())
        return int(time.mktime(t_python.timetuple()) * 1000)

    ts = property(calculate_ts)

    def __str__(self):
        return 'sensor: {}, measure time: {}, value: {}, time stamp: {}'.format(self.sensor, self.measure_time,
                                                                                self.val, self.ts)


class HistoryValue(models.Model):
    """
    represent one value measurement
    """
    sensor = models.ForeignKey(ControllerObject, on_delete=models.CASCADE)
    measure_time = models.DateTimeField(db_index=True)
    val = models.FloatField()

    def calculate_ts(self):
        t_python = self.measure_time
        t_python = timezone.make_naive(t_python, timezone=timezone.get_current_timezone())
        return int(time.mktime(t_python.timetuple()) * 1000)

    ts = property(calculate_ts)

    def __str__(self):
        return 'sensor: {}, measure time: {}, value: {}, time stamp: {}'.format(self.sensor, self.measure_time,
                                                                                self.val, self.ts)


class Relay(ControllerObject):
    """
    represent one relay, its name, state and wanted state
    """
    pin = models.PositiveSmallIntegerField(null=True)
    default_state = models.BooleanField(default=False, help_text=
        'whenever greenhouse_controller is started, this is ' \
        'the value that will be set to the relay, untill some ' \
        'controller will change this according to events or manual controll')
    simulate = models.BooleanField(default=True)
    inverted = models.BooleanField(default=False)

    def get_unit(self):
        return Units.Bool
    unit = property(get_unit)

    def __str__(self):
        return f'{self.name} at pin {self.pin}'


class Configuration(PolymorphicModel):
    name = models.CharField(max_length=128, unique=True)


class ConfigurationInt(Configuration):
    value = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.name} = {self.value}'


class ConfigurationStr(Configuration):
    value = models.CharField(max_length=256, default='')

    def __str__(self):
        return f'{self.name} = "{self.value}"'


class KeepAlive(models.Model):
    """
    keep-alive form some component
    component-name, last_ka_timestamp
    """
    name = models.CharField(max_length=128, unique=True)
    timestamp = models.DateTimeField(db_index=True)

    def calculate_is_alive(self):
        current_time = timezone.make_naive(value=timezone.now(), timezone=timezone.get_current_timezone())
        naive_timestamp = timezone.make_naive(value=self.timestamp, timezone=timezone.get_current_timezone())
        if current_time - naive_timestamp > timedelta(seconds=60):
            return False
        else:
            return True

    alive = property(calculate_is_alive)

    def __str__(self):
        return 'name: {}, timestamp: {}, alive: {}'.format(self.name, self.timestamp, self.alive)


class Event(PolymorphicModel):
    """
    base class for events models
    """
    pass


class EventAtTimeT(Event):
    """
    event that fires at time event_time
    """
    event_time = models.TimeField(help_text='Time to fire event')

    def __str__(self):
        return f'At {self.event_time}'


class EventEveryDT(Event):
    event_delta_t = models.DurationField(default=timedelta)

    def __str__(self):
        return f'Every {self.event_delta_t}'


class EventAtTimeTDays(EventAtTimeT):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    event_days = MultiSelectField(choices=DAYS_OF_WEEK)

    def __str__(self):
        return f'EventAtTimeTDays {self.event_time} Days {self.event_days}'


class Condition(PolymorphicModel):
    """
    base class for conditions models
    """

    def get_name(self):
        return self.__str__()

    name = property(get_name)


class ConditionSensorValEq(Condition):
    sensor = models.ForeignKey(ControllerObject, on_delete=models.CASCADE)
    val = models.FloatField()

    def __str__(self):
        return f'Check if {self.sensor} value is {self.val}'


class ConditionSensorValBigger(Condition):
    sensor = models.ForeignKey(ControllerObject, on_delete=models.CASCADE)
    val = models.FloatField()

    def __str__(self):
        return f'Check if {self.sensor} value is bigger than {self.val}'


class ConditionSensorValSmaller(Condition):
    sensor = models.ForeignKey(ControllerObject, on_delete=models.CASCADE)
    val = models.FloatField()

    def __str__(self):
        return f'Check if {self.sensor} value is smaller than {self.val}'


class Action(PolymorphicModel):
    """
    base class for Actions models
    """
    def get_name(self):
        return self.__str__()
    name = property(get_name)


class ActionSaveSensorValToDB(Action):
    sensor = models.ForeignKey(ControllerObject, on_delete=models.CASCADE)

    def __str__(self):
        return f'Save sensor value of {self.sensor} to the database'


class ActionSetRelayState(Action):
    relay = models.ForeignKey(Relay, on_delete=models.CASCADE)
    state = models.BooleanField(default=False, help_text='Should relay be turned ON or OFF')

    def __str__(self):
        return f'Set the relay state of {self.relay} to {self.state}'


class ActionSendEmail(Action):
    address = models.EmailField()
    subject = models.CharField(max_length=256, default='')
    message = models.CharField(max_length=256, default='')

    def __str__(self):
        return f'Send an email from {self.address} with subject "{self.subject}" and message "{self.message}"'


class ActionCaptureImageAndSave(Action):
    simulate = models.BooleanField(default=False)

    def __str__(self):
        return f'Capture image and save'


class ActionWait(Action):
    wait_time = models.DurationField(default=timedelta)

    def __str__(self):
        return f'wait for {self.wait_time}'


class Flow(models.Model):
    name = models.CharField(
        max_length=100,
    )

    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)
    conditions = models.ManyToManyField(Condition, through='FlowConditionsDefinition')
    actions = models.ManyToManyField(Action, through='FlowActionsDefinition')

    def __str__(self):
        return self.name


class FlowActionsDefinition(models.Model):
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE)


class FlowConditionsDefinition(models.Model):
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE)


class ActionRunRequest(models.Model):
    action_to_run = models.OneToOneField(Action, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()


class Command(models.Model):
    timestamp = models.DateTimeField()
    command_data = models.TextField()


