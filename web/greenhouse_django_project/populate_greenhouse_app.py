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
    r.default_state = 1
    r.save(using=dbname)

    print('creating relay: (name=light2, pin=13, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='light2')[0]
    r.pin = 1
    r.default_state = 1
    r.save(using=dbname)

    print('creating relay: (name=fan, pin=15, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='fan')[0]
    r.pin = 2
    r.default_state = 1
    r.save(using=dbname)

    print('creating relay: (name=pump, pin=5, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='pump')[0]
    r.pin = 4
    r.default_state = 1
    r.simulate = 1
    r.inverted = 1
    r.save(using=dbname)


def populate_flows(dbname):


    # populate flow at time T
    # f = Flow.objects.using(dbname).get_or_create(
    #     name=f'save sensor {a.sensor.name} data flow',
    #     event=e
    # )[0]
    # f.actions.set((a,))
    # f.save()
    #
    # populate flow every DT

    e = EventEveryDT.objects.using(dbname).get(event_delta_t=timedelta(seconds=60))
    a = ActionSaveSensorValToDB.objects.using(dbname).get(sensor=Sensor.objects.using(dbname).get(name='DS18B20_water'))
    f = Flow.objects.using(dbname).get_or_create(
        name=f'save sensor DS18B20_water data flow',
        event=e,
    )[0]
    f.actions.add(a)
    f.save(using=dbname)

    print('populating watering flow')
    e = EventAtTimeTDays.objects.using(dbname).get(event_time='08:00:00', event_days=[1, 3, 6])
    r = Relay.objects.using(dbname).get(name='pump')
    a_pump_on = ActionSetRelayState.objects.using(dbname).get(relay=r, state=1)
    a_pump_off = ActionSetRelayState.objects.using(dbname).get(relay=r, state=0)
    a_wait_for_relay_state_change = ActionWait.objects.using(dbname).get(wait_time=timedelta(seconds=10))
    a_wait_for_watering = ActionWait.objects.using(dbname).get(wait_time=timedelta(minutes=10))
    a_save_pump_relay_state_to_db = ActionSaveSensorValToDB.objects.using(dbname).get(sensor=r)

    f = Flow.objects.using(dbname).get_or_create(
        name=f'watering flow',
        event=e,
    )[0]
    f.actions.add(a_pump_on, through_defaults={})
    f.actions.add(a_wait_for_relay_state_change)
    f.actions.add(a_save_pump_relay_state_to_db)
    f.actions.add(a_wait_for_watering)
    f.actions.add(a_pump_off)
    # In order to add the same action twice, managed only by explicitly creating the FlowActionsDefinition connection
    fad = FlowActionsDefinition.objects.using(dbname).create(
        action=a_wait_for_relay_state_change,
        flow=f
    )
    fad.save(using=dbname)
    f.actions.add(a_save_pump_relay_state_to_db, through_defaults={})
    fad = FlowActionsDefinition.objects.using(dbname).create(
        action=a_save_pump_relay_state_to_db,
        flow=f
    )
    fad.save(using=dbname)
    f.save(using=dbname)


def populate_events(dbname):
    # event every dt
    dt = timedelta(seconds=60)
    e = EventEveryDT.objects.using(dbname).get_or_create(
        event_delta_t=dt
    )[0]
    e.save(using=dbname)

    # event at time t
    t = '13:00:00'
    e = EventAtTimeT.objects.using(dbname).get_or_create(
        event_time=t)[0]
    e.save(using=dbname)

    # event at time t days
    e = EventAtTimeTDays.objects.using(dbname).get_or_create(
        event_time='08:00:00',
        event_days=[1, 3, 6]
    )[0]
    e.save(using=dbname)


def populate_actions(dbname):
    r = Relay.objects.using(dbname).get(name='pump')
    a = ActionSetRelayState.objects.using(dbname).get_or_create(
        relay=r,
        state=0
    )[0]
    a.save(using=dbname)

    a = ActionSetRelayState.objects.using(dbname).get_or_create(
        relay=r,
        state=1
    )[0]
    a.save(using=dbname)

    a = ActionSaveSensorValToDB.objects.using(dbname).get_or_create(
        sensor=r,
    )[0]
    a.save(using=dbname)

    a = ActionCaptureImageAndSave.objects.using(dbname).get_or_create(
        simulate=True
    )[0]
    a.save(using=dbname)

    a = ActionWait.objects.using(dbname).get_or_create(
        wait_time=timedelta(seconds=10)
    )[0]
    a.save(using=dbname)

    a = ActionWait.objects.using(dbname).get_or_create(
        wait_time=timedelta(minutes=10)
    )[0]
    a.save(using=dbname)

    s = Sensor.objects.using(dbname).get(name='DS18B20_water')
    a = ActionSaveSensorValToDB.objects.using(dbname).get_or_create(
        sensor=s,
    )[0]
    a.save(using=dbname)


if __name__ == '__main__':
    print("Starting population script...")
    dbs = ['default']
    for db in dbs:
        print('starting DB: {}'.format(db))
        populate_sensors(db)
        populate_relays(db)
        populate_events(db)
        populate_actions(db)
        populate_flows(db)
