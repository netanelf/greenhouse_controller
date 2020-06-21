import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')
from datetime import timedelta
import django
django.setup()
from django.utils import timezone
from greenhouse_app.models import Sensor, SensorKind, Relay, TimeGovernor, Configuration


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

    print('creating sensor: {}'.format('dht_temp'))
    s = Sensor.objects.using(dbname).get_or_create(name='dht_temp')[0]
    s.kind = dht_22_temp
    s.simulate = False
    s.pin = 37
    s.i2c = False
    s.save(using=dbname)

    print('creating sensor: {}'.format('dht_humidity'))
    s = Sensor.objects.using(dbname).get_or_create(name='dht_humidity')[0]
    s.kind = dht_22_humidity
    s.simulate = False
    s.pin = 37
    s.i2c = False
    s.save(using=dbname)


    print('creating sensor: {}'.format('DS18B20_temp'))
    Sensor.objects.using(dbname).get_or_create(name='DS18B20_temp', kind=ds18b20, simulate=False, pin=99, i2c=False, device_id='28-011581dabaff')[0]

    #print 'creating sensor: {}'.format('TSL2561_lux')
    #Sensor.objects.using(dbname).get_or_create(name='lux', kind=tsl2561, simulate=False, pin=99, i2c=True, device_id='0x39')[0]


def populate_relays(dbname):

    t3 = TimeGovernor.objects.using(dbname).get_or_create(name='pump_governer',
                                                          kind='R',
                                                          on_start_time='19:00:00',
                                                          on_end_time='06:00:00',
                                                          recurring_on_start_time='2019-09-21 05:30:00',
                                                          recurring_on_period=timedelta(minutes=10),
                                                          recurring_off_period=(timedelta(days=2) - timedelta(minutes=10))
                                                          )[0]
    
    print('creating relay: (name=pump, pin=5, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='pump1')[0]
    r.pin = 4
    r.state = 1
    r.wanted_state = 1
    r.inverted = 1
    r.time_governor = t3
    r.save(using=dbname)


def populate_configurations(dbname):
    c = Configuration.objects.using(dbname).get_or_create(name='manual_mode')[0]
    c.value = 0
    c.explanation = 'if set to 1, governors do not change relay states, only manual user changes'
    c.save(using=dbname)


if __name__ == '__main__':
    print("Starting population script...")
    dbs = ['default', 'backup']
    for db in dbs:
        print("Starting db: {} ".format(db))
        populate_sensors(db)
        populate_relays(db)
        populate_configurations(db)
