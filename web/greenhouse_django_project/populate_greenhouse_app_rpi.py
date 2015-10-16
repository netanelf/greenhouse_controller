import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')

import django
django.setup()

from greenhouse_app.models import Sensor, SensorKind, Relay, TimeGovernor, Configurations


def populate_sensors():

    dht_22_temp = SensorKind.objects.get_or_create(kind='dht22temp')[0]
    dht_22_humidity = SensorKind.objects.get_or_create(kind='dht22humidity')[0]
    thermocouple = SensorKind.objects.get_or_create(kind='thermocouple')[0]

    print 'creating sensor: {}'.format('dht22_temp_door')
    s = Sensor.objects.get_or_create(name='dht22_temp_door')[0]
    s.kind = dht_22_temp
    s.simulate = False
    s.pin = 8
    s.i2c = False
    s.save()

    print 'creating sensor: {}'.format('dht22_humidity_door')
    s = Sensor.objects.get_or_create(name='dht22_humidity_door')[0]
    s.kind = dht_22_humidity
    s.simulate = False
    s.pin = 8
    s.i2c = False
    s.save()

    print 'creating sensor: {}'.format('dht22_temp_window')
    Sensor.objects.get_or_create(name='dht22_temp_window', kind=dht_22_temp, simulate=False, pin=15, i2c=False)[0]

    print 'creating sensor: {}'.format('dht22_humidity_window')
    Sensor.objects.get_or_create(name='dht22_humidity_window', kind=dht_22_humidity, simulate=False, pin=15, i2c=False)[0]

    print 'creating sensor: {}'.format('thermocouple_temp_water')
    Sensor.objects.get_or_create(name='thermocouple_temp_water', kind=thermocouple, simulate=True, pin=3, i2c=False)[0]

    print 'creating sensor: {}'.format('thermocouple_temp_light_heatsink')
    Sensor.objects.get_or_create(name='thermocouple_temp_light_heatsink', kind=thermocouple, simulate=True, pin=5, i2c=False)[0]


def populate_relays():

    t = TimeGovernor.objects.get_or_create(name='light1', kind='R', on_start_time='08:00:00', on_end_time='08:00:00', recurring_on_start_time='08:00:00', recurring_on_period=60, recurring_off_period=30)[0]
    t2 = TimeGovernor.objects.get_or_create(name='rec_90_90', kind='R', on_start_time='08:00:00', on_end_time='08:00:00', recurring_on_start_time='08:00:00', recurring_on_period=90, recurring_off_period=90)[0]
    
    print 'creating relay: (name=light1, pin=0, state=1, wanted_state=1)'
    r = Relay.objects.get_or_create(name='light1')[0]
    r.pin = 0
    r.state = 1
    r.wanted_state = 1
    r.time_governor = t
    r.save()

    print 'creating relay: (name=light2, pin=1, state=1, wanted_state=1)'
    r = Relay.objects.get_or_create(name='light2')[0]
    r.pin = 1
    r.state = 1
    r.wanted_state = 1
    r.save()

    print 'creating relay: (name=fan, pin=2, state=1, wanted_state=1)'
    r = Relay.objects.get_or_create(name='fan')[0]
    r.pin = 2
    r.state = 1
    r.wanted_state = 1
    r.save()

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
    
    
def populate_configurations():
    c = Configurations.objects.get_or_create(name='manual_mode')[0]
    c.value=0
    c.explanation='if set to 1, governors do not change relay states, only manual user changes'
    c.save()


if __name__ == '__main__':
    print "Starting population script..."
    populate_sensors()
    populate_relays()
    populate_configurations()
