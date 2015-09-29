from django.db import models


class SensorKind(models.Model):
    kind = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return 'kind: {}'.format(self.kind)


class Sensor(models.Model):
    """
    represent one sensor
    """
    name = models.CharField(max_length=128, unique=True)
    kind = models.ForeignKey(SensorKind, null=True)
    simulate = models.BooleanField(default=True)
    pin = models.PositiveSmallIntegerField(null=True)
    i2c = models.BooleanField(default=False)

    def __unicode__(self):
        return 'name: {}, kind: {}, simulate: {}, pin: {}, i2c: {}'.format(self.name, self.kind, self.simulate, self.pin, self.i2c)


class Measure(models.Model):
    """
    represent one value measurement
    """
    sensor = models.ForeignKey(Sensor)
    time = models.TimeField()
    val = models.FloatField()

    def __unicode__(self):
        return 'sensor: {}, time: {}, value: {}'.format(self.sensor, self.time, self.val)
