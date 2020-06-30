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

    #print 'creating sensor: {}'.format('TSL2561_lux')
    #Sensor.objects.using(dbname).get_or_create(name='lux', kind=tsl2561, simulate=False, pin=99, i2c=True, device_id='0x39')[0]


def populate_relays(dbname):
    print('creating relay: (name=pump, pin=5, state=1, wanted_state=1)')
    r = Relay.objects.using(dbname).get_or_create(name='pump1')[0]
    r.pin = 4
    r.state = 1
    r.inverted = 1
    r.save(using=dbname)


def populate_configurations(dbname):
    c = Configuration.objects.using(dbname).get_or_create(name='manual_mode')[0]
    c.value = 0
    c.explanation = 'if set to 1, governors do not change relay states, only manual user changes'
    c.save(using=dbname)


def populate_actions(dbname):
    r = Relay.objects.using(dbname).get(name='pump1')
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

    a = ActionCaptureImageAndSave.objects.using(dbname).get_or_create(
    )[0]
    a.save()


if __name__ == '__main__':
    print("Starting population script...")
    dbs = ['default', 'backup']
    for db in dbs:
        print("Starting db: {} ".format(db))
        populate_sensors(db)
        populate_relays(db)
        populate_configurations(db)
        populate_actions(db)
