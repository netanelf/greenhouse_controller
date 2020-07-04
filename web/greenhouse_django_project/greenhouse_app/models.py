from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
from polymorphic.models import PolymorphicModel
from multiselectfield import MultiSelectField
import time
import logging


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


class Dht22HumiditySensor(Sensor):
    pin = models.PositiveSmallIntegerField()


class Ds18b20Sensor(Sensor):
    device_id = models.CharField(max_length=32, default='', help_text='Sensor unique ID')


class Tsl2561Sensor(Sensor):
    device_id = models.CharField(max_length=32, default='', help_text='I2C address')


class DigitalInputSensor(Sensor):
    pin = models.PositiveSmallIntegerField()


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
    initial_state = models.BooleanField(default=False)
    simulate = models.BooleanField(default=True)
    inverted = models.BooleanField(default=False)

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
    pass


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


class Flow(models.Model):
    name = models.CharField(
        max_length=100,
    )

    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)
    conditions = models.ManyToManyField(Condition, blank=True)
    actions = models.ManyToManyField(Action)

    def __str__(self):
        return self.name


class ActionRunRequest(models.Model):
    action_to_run = models.OneToOneField(Action, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()


