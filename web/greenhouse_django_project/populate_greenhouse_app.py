import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')

import django
django.setup()

from greenhouse_app.models import Sensor, SensorKind


def populate():

    dht_22_temp = SensorKind.objects.get_or_create(kind='dht22temp')[0]
    dht_22_humidity = SensorKind.objects.get_or_create(kind='dht22humidity')[0]
    thermocouple = SensorKind.objects.get_or_create(kind='thermocouple')[0]

    print 'creating sensor: {}'.format('dht22_temp_door')
    Sensor.objects.get_or_create(name='dht22_temp_door', kind=dht_22_temp, simulate=True, pin=1, i2c=False)[0]

    print 'creating sensor: {}'.format('dht22_humidity_door')
    Sensor.objects.get_or_create(name='dht22_humidity_door', kind=dht_22_humidity, simulate=True, pin=1, i2c=False)[0]

    print 'creating sensor: {}'.format('thermocouple_temp_water')
    Sensor.objects.get_or_create(name='thermocouple_temp_water', kind=thermocouple, simulate=True, pin=3, i2c=False)[0]

    print 'creating sensor: {}'.format('thermocouple_temp_light_heatsink')
    Sensor.objects.get_or_create(name='thermocouple_temp_light_heatsink', kind=thermocouple, simulate=True, pin=4, i2c=False)[0]


if __name__ == '__main__':
    print "Starting Rango population script..."
    populate()
