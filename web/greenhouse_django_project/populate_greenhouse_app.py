import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')

import django
django.setup()

from greenhouse_app.models import Sensor, SensorKind, Relay, TimeGovernor


def populate_sensors():

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


def populate_relays():

    t = TimeGovernor.objects.get_or_create(name='light1', kind='R', on_start_time='08:00:00', on_end_time='08:00:00', recurring_on_start_time='08:00:00', recurring_on_period=60, recurring_off_period=30)[0]

    print 'creating relay: (name=light1, pin=1, state=1, wanted_state=1, simulate=1)'
    Relay.objects.get_or_create(name='light1', pin=1, state=1, wanted_state=1, simulate=1, time_governor=t)

    print 'creating relay: (name=light2, pin=2, state=1, wanted_state=1, simulate=1)'
    Relay.objects.get_or_create(name='light2', pin=2, state=1, wanted_state=1, simulate=1)

    print 'creating relay: (name=fan, pin=3, state=1, wanted_state=1, simulate=1)'
    Relay.objects.get_or_create(name='fan', pin=3, state=1, wanted_state=1, simulate=1)

    print 'creating relay: (name=humidity, pin=4, state=1, wanted_state=1, simulate=1)'
    Relay.objects.get_or_create(name='humidity', pin=4, state=1, wanted_state=1, simulate=1)


if __name__ == '__main__':
    print "Starting population script..."
    populate_sensors()
    populate_relays()
