import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')

import django
django.setup()
from greenhouse_app.models import Sensor, SensorKind, Relay, TimeGovernor, Configuration


def populate_sensors(dbname):
    print 'deleting data in SensorKind'
    SensorKind.objects.using(dbname).all().delete()
    print 'deleting data in Sensor'
    Sensor.objects.using(dbname).all().delete()
    print 'deleting data in TimeGovernors'
    TimeGovernor.objects.using(dbname).all().delete()

    dht_22_temp = SensorKind.objects.using(dbname).get_or_create(kind='dht22temp')[0]
    dht_22_humidity = SensorKind.objects.using(dbname).get_or_create(kind='dht22humidity')[0]
    ds18b20 = SensorKind.objects.using(dbname).get_or_create(kind='ds18b20')[0]
    tsl2561 = SensorKind.objects.using(dbname).get_or_create(kind='tsl2561')[0]

    print 'creating sensor: {}'.format('dht22_temp_door')
    s = Sensor.objects.using(dbname).get_or_create(name='dht22_temp_door')[0]
    s.kind = dht_22_temp
    s.simulate = True
    s.pin = 8
    s.i2c = False
    s.save(using=dbname)

    print 'creating sensor: {}'.format('dht22_humidity_door')
    s = Sensor.objects.using(dbname).get_or_create(name='dht22_humidity_door')[0]
    s.kind = dht_22_humidity
    s.simulate = True
    s.pin = 8
    s.i2c = False
    s.save(using=dbname)

    print 'creating sensor: {}'.format('dht22_temp_window')
    Sensor.objects.using(dbname).get_or_create(name='dht22_temp_window', kind=dht_22_temp, simulate=True, pin=15, i2c=False)[0]

    print 'creating sensor: {}'.format('dht22_humidity_window')
    Sensor.objects.using(dbname).get_or_create(name='dht22_humidity_window', kind=dht_22_humidity, simulate=True, pin=15, i2c=False)[0]

    print 'creating sensor: {}'.format('DS18B20_water')
    Sensor.objects.using(dbname).get_or_create(name='DS18B20_water', kind=ds18b20, simulate=True, pin=99, i2c=False, device_id='28-031467d282ff')[0]

    print 'creating sensor: {}'.format('DS18B20_indoor')
    Sensor.objects.using(dbname).get_or_create(name='DS18B20_indoor', kind=ds18b20, simulate=True, pin=99, i2c=False, device_id='28-031467eefbff')[0]

    print 'creating sensor: {}'.format('TSL2561_lux_1')
    Sensor.objects.using(dbname).get_or_create(name='lux_1', kind=tsl2561, simulate=True, pin=99, i2c=True, device_id='0x39')[0]


def populate_relays(dbname):

    t = TimeGovernor.objects.using(dbname).get_or_create(name='light1', kind='O', on_start_time='21:55:00', on_end_time='22:00:00', recurring_on_start_time='08:00:00', recurring_on_period=60, recurring_off_period=30)[0]
    t2 = TimeGovernor.objects.using(dbname).get_or_create(name='rec_90_90', kind='R', on_start_time='08:00:00', on_end_time='08:00:00', recurring_on_start_time='08:00:00', recurring_on_period=90, recurring_off_period=90)[0]

    print 'creating relay: (name=light1, pin=11, state=1, wanted_state=1)'
    r = Relay.objects.using(dbname).get_or_create(name='light1')[0]
    r.pin = 0
    r.state = 1
    r.wanted_state = 1
    r.time_governor = t
    r.save(using=dbname)

    print 'creating relay: (name=light2, pin=13, state=1, wanted_state=1)'
    r = Relay.objects.using(dbname).get_or_create(name='light2')[0]
    r.pin = 1
    r.state = 1
    r.wanted_state = 1
    r.save(using=dbname)

    print 'creating relay: (name=fan, pin=15, state=1, wanted_state=1)'
    r = Relay.objects.using(dbname).get_or_create(name='fan')[0]
    r.pin = 2
    r.state = 1
    r.wanted_state = 1
    r.save(using=dbname)
    '''
    print 'creating relay: (name=humidity, pin=3, state=1, wanted_state=1)'
    r = Relay.objects.get_or_create(name='humidity')[0]
    r.pin = 3
    r.state = 1
    r.wanted_state = 1
    r.save()

    print 'creating relay: (name=humidity, pin=4, state=1, wanted_state=1)'
    r = Relay.objects.get_or_create(name='fan2')[0]
    r.pin = 4
    r.state = 1
    r.wanted_state = 1
    r.save()

    print 'creating relay: (name=misc0, pin=5, state=1, wanted_state=1)'
    r = Relay.objects.get_or_create(name='misc0')[0]
    r.pin = 5
    r.state = 1
    r.wanted_state = 1
    r.save()

    print 'creating relay: (name=misc1, pin=6, state=1, wanted_state=1)'
    r = Relay.objects.get_or_create(name='misc1')[0]
    r.pin = 6
    r.state = 1
    r.wanted_state = 1
    r.time_governor = t2
    r.save()

    print 'creating relay: (name=misc2, pin=7, state=1, wanted_state=1)'
    r = Relay.objects.get_or_create(name='misc2')[0]
    r.pin = 7
    r.state = 1
    r.wanted_state = 1
    r.time_governor = t2
    r.save()
    '''


def populate_configurations(dbname):
    c = Configuration.objects.using(dbname).get_or_create(name='manual_mode')[0]
    c.value=0
    c.explanation='if set to 1, governors do not change relay states, only manual user changes'
    c.save(using=dbname)


if __name__ == '__main__':
    print "Starting population script..."
    dbs = ['default']
    for db in dbs:
        print 'starting DB: {}'.format(db)
        populate_sensors(db)
        populate_relays(db)
        populate_configurations(db)
