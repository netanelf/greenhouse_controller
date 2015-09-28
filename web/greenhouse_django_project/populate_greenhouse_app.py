import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')

import django
django.setup()

from greenhouse_app.models import Sensor


def populate():
    names = ['dht22_temp_door', 'dht22_humidity_door', 'thermocouple_temp_water', 'thermocouple_temp_light_heatsink']
    for name in names:
        print 'creating sensor: {}'.format(name)
        add_sensor(name=name)


def add_sensor(name):
    Sensor.objects.get_or_create(name=name)


# Start execution here!
if __name__ == '__main__':
    print "Starting Rango population script..."
    populate()
