import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')

import django
django.setup()
from django.utils import timezone
from datetime import timedelta
from greenhouse_app.models import Sensor, SensorKind, Relay, TimeGovernor, Configuration, EventAtTimeT, ActionSaveSensorValToDB


def populate_sensors(dbname):
    print('deleting data in SensorKind')
    SensorKind.objects.using(dbname).all().delete()
    print('deleting data in Sensor')
    Sensor.objects.using(dbname).all().delete()
    print('deleting data in TimeGovernors')
    TimeGovernor.objects.using(dbname).all().delete()

    dht_22_temp = SensorKind.objects.using(dbname).get_or_create(kind='dht22temp')[0]
    dht_22_humidity = SensorKind.objects.using(dbname).get_or_create(kind='dht22humidity')[0]
    ds18b20 = SensorKind.objects.using(dbname).get_or_create(kind='ds18b20')[0]
    tsl2561 = SensorKind.objects.using(dbname).get_or_create(kind='tsl2561')[0]
    digitalInput = SensorKind.objects.using(dbname).get_or_create(kind='digitalInput')[0]

    print('creating sensor: {}'.format('dht22_temp_door'))
    s = Sensor.objects.using(dbname).get_or_create(name='dht22_temp_door')[0]
    s.kind = dht_22_temp
    s.simulate = True
    s.pin = 8
    s.i2c = False
    s.save(using=dbname)

    print('creating sensor: {}'.format('dht22_humidity_door'))
    s = Sensor.objects.using(dbname).get_or_create(name='dht22_humidity_door')[0]
    s.kind = dht_22_humidity
    s.simulate = True
    s.pin = 8
    s.i2c = False
    s.save(using=dbname)

    print('creating sensor: {}'.format('dht22_temp_window'))
    Sensor.objects.using(dbname).get_or_create(name='dht22_temp_window', kind=dht_22_temp, simulate=True, pin=15, i2c=False)[0]

    print('creating sensor: {}'.format('dht22_humidity_window'))
    Sensor.objects.using(dbname).get_or_create(name='dht22_humidity_window', kind=dht_22_humidity, simulate=True, pin=15, i2c=False)[0]

    print('creating sensor: {}'.format('DS18B20_water'))
    Sensor.objects.using(dbname).get_or_create(name='DS18B20_water', kind=ds18b20, simulate=True, pin=99, i2c=False, device_id='28-031467d282ff')[0]

    print('creating sensor: {}'.format('DS18B20_indoor'))
    Sensor.objects.using(dbname).get_or_create(name='DS18B20_indoor', kind=ds18b20, simulate=True, pin=99, i2c=False, device_id='28-031467eefbff')[0]

    print('creating sensor: {}'.format('TSL2561_lux_1'))
    Sensor.objects.using(dbname).get_or_create(name='lux_1', kind=tsl2561, simulate=True, pin=99, i2c=True, device_id='0x39')[0]

    print('creating sensor: {}'.format('DigitalInput_water_low_level'))
    Sensor.objects.using(dbname).get_or_create(name='water_low_level', kind=digitalInput, simulate=True, pin=10, i2c=False)[0]


def populate_relays(dbname):

    t = TimeGovernor.objects.using(dbname).get_or_create(name='light1',
                                                         kind='O',
                                                         on_start_time='21:55:00',
                                                         on_end_time='22:00:00',
                                                         recurring_on_start_time=timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                         recurring_on_period=timedelta(seconds=90),
                                                         recurring_off_period=timedelta(seconds=90)
                                                         )[0]

    t2 = TimeGovernor.objects.using(dbname).get_or_create(name='rec_90_90',
                                                          kind='R',
                                                          on_start_time='08:00:00',
                                                          on_end_time='08:00:00',
                                                          recurring_on_start_time=timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                          recurring_on_period=timedelta(seconds=90),
                                                          recurring_off_period=timedelta(seconds=90)
                                                          )[0]

    print('creating relay: (name=light1, pin=11, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='light1')[0]
    r.pin = 0
    r.state = 1
    r.wanted_state = 1
    r.time_governor = t
    r.save(using=dbname)

    print('creating relay: (name=light2, pin=13, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='light2')[0]
    r.pin = 1
    r.state = 1
    r.wanted_state = 1
    r.save(using=dbname)

    print('creating relay: (name=fan, pin=15, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='fan')[0]
    r.pin = 2
    r.state = 1
    r.wanted_state = 1
    r.save(using=dbname)

    print('creating relay: (name=pump, pin=5, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='fan')[0]
    r.pin = 4
    r.state = 1
    r.wanted_state = 1
    r.simulate = 1
    r.inverted = 1
    r.time_governor = t2
    r.save(using=dbname)


def populate_configurations(dbname):
    c = Configuration.objects.using(dbname).get_or_create(name='manual_mode')[0]
    c.value = 0
    c.explanation = 'if set to 1, governors do not change relay states, only manual user changes'
    c.save(using=dbname)


def populate_events(dbname):
    t = '17:00:00'
    e = EventAtTimeT.objects.using(dbname).get_or_create(
        name=f'picture at certain time {t}',
        event_time=t)[0]
    e.save(using=dbname)


def populate_actions(dbname):
    sensor = Sensor.objects.using(dbname).all()[0]
    a = ActionSaveSensorValToDB.objects.using(dbname).get_or_create(
        sensor=sensor,
    )[0]
    a.save()


if __name__ == '__main__':
    print("Starting population script...")
    dbs = ['default']
    for db in dbs:
        print('starting DB: {}'.format(db))
        populate_sensors(db)
        populate_relays(db)
        populate_configurations(db)
        populate_events(db)
        populate_actions(db)
