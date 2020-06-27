import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')

import django
django.setup()
from greenhouse_app.models import *


def populate_sensors(dbname):
    print('deleting data in Sensor')
    Sensor.objects.using(dbname).all().delete()

    dht_22_temp = Dht22TempSensor.objects.using(dbname).get_or_create(
        pin=8,
        simulate=True,
        name='dht22_temp_door'
    )[0]
    dht_22_temp.save(using=dbname)

    dht_22_humidity = Dht22HumiditySensor.objects.using(dbname).get_or_create(
        pin=8,
        simulate=True,
        name='dht22_humidity_door'
    )[0]
    dht_22_humidity.save(using=dbname)

    ds18b20 = Ds18b20Sensor.objects.using(dbname).get_or_create(
        device_id='28-031467d282ff',
        simulate=True,
        name='DS18B20_water'
    )[0]
    ds18b20.save(using=dbname)

    tsl2561 = Tsl2561Sensor.objects.using(dbname).get_or_create(
        device_id='0x39',
        simulate=True,
        name='lux_1'
    )[0]
    tsl2561.save(using=dbname)

    digital_input = DigitalInputSensor.objects.using(dbname).get_or_create(
        pin=10,
        simulate=True,
        name='water_low_level'
    )[0]
    digital_input.save(using=dbname)


def populate_relays(dbname):

    print('creating relay: (name=light1, pin=11, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='light1')[0]
    r.pin = 0
    r.state = 1
    r.save(using=dbname)

    print('creating relay: (name=light2, pin=13, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='light2')[0]
    r.pin = 1
    r.state = 1
    r.save(using=dbname)

    print('creating relay: (name=fan, pin=15, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='fan')[0]
    r.pin = 2
    r.state = 1
    r.save(using=dbname)

    print('creating relay: (name=pump, pin=5, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='fan')[0]
    r.pin = 4
    r.state = 1
    r.simulate = 1
    r.inverted = 1
    r.save(using=dbname)


def populate_flows(dbname):
    # populate flow at time T
    e = populate_event_at_t(dbname)
    a = populate_actions(dbname)
    f = Flow.objects.using(dbname).get_or_create(
        name=f'save sensor {a.sensor.name} data flow',
        event=e
    )[0]
    f.actions.set((a,))
    f.save()

    # populate flow every DT
    dt = timedelta(seconds=35)
    e = EventEveryDT.objects.using(dbname).get_or_create(
        event_delta_t=dt
    )[0]
    e.save(using=dbname)
    sensor = Sensor.objects.using(dbname).all()[1]
    a = ActionSaveSensorValToDB.objects.using(dbname).get_or_create(
        sensor=sensor,
    )[0]
    a.save()
    f = Flow.objects.using(dbname).get_or_create(
        name=f'save sensor {sensor.name} data flow',
        event=e
    )[0]
    f.actions.set((a,))
    f.save()


def populate_event_at_t(dbname):
    t = '13:00:00'
    e = EventAtTimeT.objects.using(dbname).get_or_create(
        event_time=t)[0]
    e.save(using=dbname)
    return e


def populate_actions(dbname):
    r = Relay.objects.using(dbname).all()[0]
    a = ActionSetRelayState.objects.using(dbname).get_or_create(
        relay=r,
        state=0
    )[0]
    a.save()

    a = ActionSetRelayState.objects.using(dbname).get_or_create(
        relay=r,
        state=1
    )[0]
    a.save()

    sensor = Sensor.objects.using(dbname).all()[0]
    sensor_name = sensor.name
    a = ActionSaveSensorValToDB.objects.using(dbname).get_or_create(
        sensor=sensor,
    )[0]
    a.save()
    return a


if __name__ == '__main__':
    print("Starting population script...")
    dbs = ['default']
    for db in dbs:
        print('starting DB: {}'.format(db))
        populate_sensors(db)
        populate_relays(db)
        populate_flows(db)
