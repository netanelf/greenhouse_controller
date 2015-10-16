from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime


class SensorKind(models.Model):
    SENSOR_KINDS = (
                    ('dht22temp', 'dht22temp'),
                    ('dht22humidity', 'dht22humidity'),
                    ('ds18b20', 'ds18b20'),
                    ('other', 'other')
    )
    kind = models.CharField(max_length=128, choices=SENSOR_KINDS, unique=True, default='other')

    def __unicode__(self):
        return self.kind


class Sensor(models.Model):
    """
    represent one sensor
    """
    name = models.CharField(max_length=128, unique=True)
    kind = models.ForeignKey(SensorKind, blank=True, null=True)
    simulate = models.BooleanField(default=True)
    pin = models.PositiveSmallIntegerField(default=99)
    i2c = models.BooleanField(default=False)
    device_id = models.CharField(max_length=32, default='')
    
    def __unicode__(self):
        return self.name


class Measure(models.Model):
    """
    represent one value measurement
    """
    sensor = models.ForeignKey(Sensor)
    time = models.DateTimeField()
    val = models.FloatField()

    def __unicode__(self):
        return 'sensor: {}, time: {}, value: {}'.format(self.sensor, self.time, self.val)


class TimeGovernor(models.Model):
    """
    """
    GOVERNOR_KINDS = (
        ('R', 'recurring'),
        ('O', 'on off'),
    )
    name = models.CharField(max_length=128, unique=True)

    kind = models.CharField(max_length=1, choices=GOVERNOR_KINDS)

    on_start_time = models.TimeField()
    on_end_time = models.TimeField()

    recurring_on_start_time = models.TimeField()
    recurring_on_period = models.IntegerField()  # seconds
    recurring_off_period = models.IntegerField()  # seconds

    def on_off_status(self):
        """
        return the output of this governor (should the relay be in ON or OFF state)
        """
        if self.kind == 'R':
            t = timezone.now()
            t_0 = datetime(year=t.year, month=t.month, day=t.day, hour=self.recurring_on_start_time.hour,
                           minute=self.recurring_on_start_time.minute,
                           second=self.recurring_on_start_time.second,
                           microsecond=0, tzinfo=t.tzinfo)
            tdelta = t - t_0
            delta_seconds = tdelta.total_seconds()
            period = self.recurring_on_period + self.recurring_off_period
            a, b = divmod(delta_seconds, period)
            shited_t = t - timedelta(seconds=a * period)
            d = shited_t - t_0
            if 0 <= d.total_seconds() < self.recurring_on_period:
                return 1
            else:
                return 0

        elif self.kind == 'O':
            t = timezone.now()
            t = timezone.make_naive(t, timezone=timezone.get_current_timezone())
            t = t.time()  # take only time part of date + time
            if self.on_start_time < t < self.on_end_time:
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


class Relay(models.Model):
    """
    represent one relay, its name, state and wanted state
    """
    name = models.CharField(max_length=128, unique=True)
    pin = models.PositiveSmallIntegerField(null=True)
    state = models.BooleanField(default=False)
    wanted_state = models.BooleanField(default=False)
    simulate = models.BooleanField(default=True)
    time_governor = models.ForeignKey(TimeGovernor, null=True)

    def __unicode__(self):
        return self.name


class Configurations(models.Model):
    name = models.CharField(max_length=128, unique=True)
    value = models.IntegerField(default=0)
    explanation = models.CharField(max_length=256, default='')

    def __unicode__(self):
        return self.name
