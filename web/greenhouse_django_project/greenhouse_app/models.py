from django.db import models


class Sensor(models.Model):
    """
    represent one sensor
    """
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name


class Measure(models.Model):
    """
    represent one value measurement
    """
    sensor = models.ForeignKey(Sensor)
    time = models.TimeField()
    val = models.FloatField()

    def __unicode__(self):
        return 'sensor: {}, time: {}, value: {}'.format(self.sensor, self.time, self.val)
