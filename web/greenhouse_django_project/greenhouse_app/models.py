from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
import time
import logging


class SensorKind(models.Model):
    SENSOR_KINDS = (
                    ('dht22temp', 'dht22temp'),
                    ('dht22humidity', 'dht22humidity'),
                    ('ds18b20', 'ds18b20'),
                    ('tsl2561', 'tsl2561'),
                    ('digitalInput', 'digitalInput'),
                    ('other', 'other')
    )
    kind = models.CharField(max_length=128, choices=SENSOR_KINDS, unique=True, default='other')

    def __unicode__(self):
        return self.kind


class ControllerOBject(models.Model):
    """
    represent a controller object ie. sensor or relay
    this way we can connect a measure to a relay or a sensor
    """
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name


class Sensor(ControllerOBject):
    """
    represent one sensor
    """
    kind = models.ForeignKey(SensorKind, blank=True, null=True, on_delete=models.CASCADE)
    simulate = models.BooleanField(default=True)
    pin = models.PositiveSmallIntegerField(default=99)
    i2c = models.BooleanField(default=False)
    device_id = models.CharField(max_length=32, default='')
    
    #def __unicode__(self):
    #    return self.name


class Measure(models.Model):
    """
    represent one value measurement
    """
    sensor = models.ForeignKey(ControllerOBject, on_delete=models.CASCADE)
    measure_time = models.DateTimeField(db_index=True)
    val = models.FloatField()

    def calculate_ts(self):
        t_python = self.measure_time
        t_python = timezone.make_naive(t_python, timezone=timezone.get_current_timezone())
        return int(time.mktime(t_python.timetuple())*1000)

    ts = property(calculate_ts)

    def __unicode__(self):
        return 'sensor: {}, measure time: {}, value: {}, time stamp: {}'.format(self.sensor, self.measure_time, self.val, self.ts)


class TimeGovernor(models.Model):
    """
    """
    logger = logging.getLogger(__name__)

    GOVERNOR_KINDS = (
        ('R', 'recurring'),
        ('O', 'on off'),
    )

    name = models.CharField(max_length=128, unique=True)
    kind = models.CharField(max_length=1, choices=GOVERNOR_KINDS)

    on_start_time = models.TimeField(help_text='used only in "on off" governor')
    on_end_time = models.TimeField(help_text='used only in "on off" governor')

    recurring_on_start_time = models.DateTimeField(help_text='used only in "on off" governor')
    recurring_on_period = models.DurationField(help_text='timedelta "DD HH:MM:SS", used only in "recurring" governor')  # seconds
    recurring_off_period = models.DurationField(help_text='timedelta "DD HH:MM:SS", used only in "recurring" governor')  # seconds

    def on_off_status(self):
        """
        return the output of this governor (should the relay be in ON or OFF state)
        """
        self.logger.debug('kind: {}'.format(self.kind))
        if self.kind == 'R':
            t = timezone.now()
            t_delta = t - self.recurring_on_start_time
            delta_seconds = t_delta.total_seconds()
            period_sec = (self.recurring_on_period + self.recurring_off_period).total_seconds()
            a, b = divmod(delta_seconds, period_sec)
            shifted_t = t - timedelta(seconds=a * period_sec)
            #print('comparing {} with float: {}'.format(self.recurring_on_period, float(self.recurring_on_period)))
            if self.recurring_on_start_time <= shifted_t < self.recurring_on_start_time + self.recurring_on_period:
                return 1
            else:
                return 0

        elif self.kind == 'O':

            t = timezone.now()
            t = timezone.make_naive(t, timezone=timezone.get_current_timezone())

            on_time_this_date = timezone.make_naive(timezone.now(), timezone=timezone.get_current_timezone())\
                .replace(hour=self.on_start_time.hour,
                         minute=self.on_start_time.minute,
                         second=self.on_start_time.second,
                         microsecond=0)

            off_time_this_date = timezone.make_naive(timezone.now(), timezone=timezone.get_current_timezone())\
                .replace(hour=self.on_end_time.hour,
                         minute=self.on_end_time.minute,
                         second=self.on_end_time.second,
                         microsecond=0)

            if self.on_end_time < self.on_start_time:
                if t.hour < 12:
                    on_time_this_date = on_time_this_date - timedelta(days=1)  # yesterday
                else:
                    off_time_this_date = off_time_this_date + timedelta(days=1) # tomorrow

            if on_time_this_date < t < off_time_this_date:
                return 1
            else:
                return 0

    def get_nice_kind(self):
        for k, v in self.GOVERNOR_KINDS:
            if k == self.kind:
                return v
        return 'UNKNOWN'

    state = property(on_off_status)
    nice_kind = property(get_nice_kind)

    def __unicode__(self):
        return self.name


class Relay(ControllerOBject):
    """
    represent one relay, its name, state and wanted state
    """
    #name = models.CharField(max_length=128, unique=True)
    pin = models.PositiveSmallIntegerField(null=True)
    state = models.BooleanField(default=False)
    wanted_state = models.BooleanField(default=False)
    simulate = models.BooleanField(default=True)
    time_governor = models.ForeignKey(TimeGovernor, null=True, on_delete=models.CASCADE)
    inverted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Configuration(models.Model):
    name = models.CharField(max_length=128, unique=True)
    value = models.IntegerField(default=0)
    explanation = models.CharField(max_length=256, default='')

    def __unicode__(self):
        return self.name


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

    def __unicode__(self):
        return 'name: {}, timestamp: {}, alive: {}'.format(self.name, self.timestamp, self.alive)


class Event(models.Model):
    """
    base class for events models
    """
    name = models.CharField(
        max_length=100,
    )


class EventAtTimeT(Event):
    """
    event that fires at time event_time
    """
    event_time = models.TimeField(help_text='Time to fire event')


class Conditions(models.Model):
    """
    base class for conditions models
    """
    name = models.CharField(
        max_length=100,
    )


class Actions(models.Model):
    """
    base class for Actions models
    """
    name = models.CharField(
        max_length=100,
    )


class SaveSensorValToDB(Actions):
    sensor = models.ForeignKey(ControllerOBject, on_delete=models.CASCADE)
    measure_time = models.DateTimeField(db_index=True)
    val = models.FloatField()
