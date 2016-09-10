import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')

import django
django.setup()
from greenhouse_app.models import Sensor, SensorKind, Relay, TimeGovernor, Configuration


def populate_sensors():
    print 'deleting data in SensorKind'
    SensorKind.objects.all().delete()
    print 'deleting data in Sensor'
    Sensor.objects.all().delete()

    dht_22_temp = SensorKind.objects.get_or_create(kind='dht22temp')[0]
    dht_22_humidity = SensorKind.objects.get_or_create(kind='dht22humidity')[0]
    ds18b20 = SensorKind.objects.get_or_create(kind='ds18b20')[0]
    tsl2561 = SensorKind.objects.get_or_create(kind='tsl2561')[0]

    print 'creating sensor: {}'.format('dht_temp')
    s = Sensor.objects.get_or_create(name='dht_temp')[0]
    s.kind = dht_22_temp
    s.simulate = False
    s.pin = 37
    s.i2c = False
    s.save()

    print 'creating sensor: {}'.format('dht_humidity')
    s = Sensor.objects.get_or_create(name='dht_humidity')[0]
    s.kind = dht_22_humidity
    s.simulate = False
    s.pin = 37
    s.i2c = False
    s.save()


    print 'creating sensor: {}'.format('DS18B20_temp')
    Sensor.objects.get_or_create(name='DS18B20_temp', kind=ds18b20, simulate=False, pin=99, i2c=False, device_id='28-011581dabaff')[0]

    print 'creating sensor: {}'.format('TSL2561_lux')
    Sensor.objects.get_or_create(name='lux', kind=tsl2561, simulate=False, pin=99, i2c=True, device_id='0x39')[0]


def populate_relays():

    t = TimeGovernor.objects.get_or_create(name='light_governer', kind='O', on_start_time='19:00:00', on_end_time='06:00:00', recurring_on_start_time='08:00:00', recurring_on_period=60, recurring_off_period=30)[0]
    t2 = TimeGovernor.objects.get_or_create(name='fan_governer', kind='R', on_start_time='19:00:00', on_end_time='06:00:00', recurring_on_start_time='08:00:00', recurring_on_period=60*5, recurring_off_period=30)[0]
    
    print 'creating relay: (name=light, pin=1, state=1, wanted_state=1)'
    r = Relay.objects.get_or_create(name='light')[0]
    r.pin = 0
    r.state = 1
    r.wanted_state = 1
    r.time_governor = t
    r.save()

    print 'creating relay: (name=fan, pin=2, state=1, wanted_state=1)'
    r = Relay.objects.get_or_create(name='fan')[0]
    r.pin = 1
    r.state = 1
    r.wanted_state = 1
    r.time_governor = t2
    r.save()

    print 'creating relay: (name=pump, pin=3, state=1, wanted_state=1)'
    r = Relay.objects.get_or_create(name='pump')[0]
    r.pin = 2
    r.state = 0
    r.wanted_state = 0
    r.save()


def populate_configurations():
    c = Configuration.objects.get_or_create(name='manual_mode')[0]
    c.value=0
    c.explanation='if set to 1, governors do not change relay states, only manual user changes'
    c.save()


if __name__ == '__main__':
    print "Starting population script..."
    populate_sensors()
    populate_relays()
    populate_configurations()
