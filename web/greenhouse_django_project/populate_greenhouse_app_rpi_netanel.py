import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')
import django
django.setup()
from greenhouse_app.models import *


def populate_sensors(dbname):
    print('deleting data in Sensor')
    Sensor.objects.using(dbname).all().delete()

    dht_22_temp = Dht22TempSensor.objects.using(dbname).get_or_create(
        pin=37,
        simulate=False,
        name='dht_temp'
    )[0]
    dht_22_temp.save(using=dbname)

    dht_22_humidity = Dht22HumiditySensor.objects.using(dbname).get_or_create(
        pin=37,
        simulate=False,
        name='dht_humidity'
    )[0]
    dht_22_humidity.save(using=dbname)

    ds18b20 = Ds18b20Sensor.objects.using(dbname).get_or_create(
        device_id='28-011581dabaff',
        simulate=False,
        name='DS18B20_temp'
    )[0]
    ds18b20.save(using=dbname)

    digital_input = DigitalInputSensor.objects.using(dbname).get_or_create(
        pin=38,
        simulate=False,
        name='water_low_level'
    )[0]
    digital_input.save(using=dbname)

    flow = FlowSensor.objects.using(dbname).get_or_create(
        pin=18,
        simulate=False,
        name='water_flow_sensor',
        mll_per_pulse=2
    )[0]
    flow.save(using=dbname)


def populate_relays(dbname):
    print('creating relay: (name=pump, pin=5, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='pump')[0]
    r.pin = 4
    r.state = 1
    r.inverted = 1
    r.simulate = False
    r.save(using=dbname)


def populate_configurations(dbname):
    c = Configuration.objects.using(dbname).get_or_create(name='manual_mode')[0]
    c.value = 0
    c.explanation = 'if set to 1, governors do not change relay states, only manual user changes'
    c.save(using=dbname)


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
        sensor=r
    )[0]
    a.save(using=dbname)

    a = ActionCaptureImageAndSave.objects.using(dbname).get_or_create(
        simulate=False
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

    a = ActionWait.objects.using(dbname).get_or_create(
        wait_time=timedelta(hours=5)
    )[0]
    a.save(using=dbname)


def populate_events(dbname):
    e = EventAtTimeTDays.objects.using(dbname).get_or_create(
        event_time='08:00:00',
        event_days=[1, 3, 6]
    )[0]
    e.save(using=dbname)

    e = EventAtTimeTDays.objects.using(dbname).get_or_create(
        event_time='07:00:00',
        event_days=[0, 1, 2, 3, 4, 5, 6]
    )[0]
    e.save(using=dbname)


def populate_flows(dbname):
    populate_watering_flow(dbname)
    populate_camera_flow(dbname)
    populate_sensors_values_saving_to_db(dbname)


def populate_sensors_values_saving_to_db(dbname):
    print('populate_sensors_values_saving_to_db flow')
    e = EventEveryDT.objects.using(dbname).get_or_create(
        event_delta_t=timedelta(minutes=15)
    )[0]
    e.save(using=dbname)
    dht_temp_sensor = Dht22TempSensor.objects.using(dbname).get(name='dht_temp')
    dht_humid_sensor = Dht22HumiditySensor.objects.using(dbname).get(name='dht_humidity')
    ds18b20_temp_sensor = Ds18b20Sensor.objects.using(dbname).get(name='DS18B20_temp')
    flow_sensor = FlowSensor.objects.using(dbname).get(name='water_flow_sensor')

    a_save_temp_dht_to_db = ActionSaveSensorValToDB.objects.using(dbname).get_or_create(sensor=dht_temp_sensor)[0]
    a_save_temp_dht_to_db.save(using=dbname)

    a_save_humidity_dht_to_db = ActionSaveSensorValToDB.objects.using(dbname).get_or_create(sensor=dht_humid_sensor)[0]
    a_save_humidity_dht_to_db.save(using=dbname)

    a_save_temp_ds18b20_to_db = ActionSaveSensorValToDB.objects.using(dbname).get_or_create(sensor=ds18b20_temp_sensor)[0]
    a_save_temp_ds18b20_to_db.save(using=dbname)

    a_save_flow_to_db = ActionSaveSensorValToDB.objects.using(dbname).get_or_create(sensor=flow_sensor)[0]
    a_save_flow_to_db.save(using=dbname)

    f = Flow.objects.using(dbname).get_or_create(
        name=f'save_sensors_to_db',
        event=e,
    )[0]
    f.actions.add(a_save_temp_dht_to_db)
    f.actions.add(a_save_humidity_dht_to_db)
    f.actions.add(a_save_temp_ds18b20_to_db)
    f.actions.add(a_save_flow_to_db)
    f.save(using=dbname)


def populate_camera_flow(dbname):
    print('populating camera flow')
    e = EventAtTimeTDays.objects.using(dbname).get(event_time='07:00:00', event_days=[0, 1, 2, 3, 4, 5, 6])
    a_take_picture = ActionCaptureImageAndSave.objects.using(dbname).get()
    a_wait_5_hrs = ActionWait.objects.using(dbname).get(wait_time=timedelta(hours=5))
    f = Flow.objects.using(dbname).get_or_create(
        name=f'camera flow',
        event=e,
    )[0]
    f.actions.add(a_take_picture)
    f.actions.add(a_wait_5_hrs)
    fad = FlowActionsDefinition.objects.using(dbname).create(
        action=a_take_picture,
        flow=f
    )
    fad.save(using=dbname)

    fad = FlowActionsDefinition.objects.using(dbname).create(
        action=a_wait_5_hrs,
        flow=f
    )
    fad.save(using=dbname)

    fad = FlowActionsDefinition.objects.using(dbname).create(
        action=a_take_picture,
        flow=f
    )
    fad.save(using=dbname)


def populate_watering_flow(dbname):
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


if __name__ == '__main__':
    print("Starting population script...")
    dbs = ['default', 'backup']
    for db in dbs:
        print("Starting db: {} ".format(db))
        populate_sensors(db)
        populate_relays(db)
        populate_actions(db)
        populate_events(db)
        populate_flows(db)
