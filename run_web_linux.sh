#!/bin/bash 

echo "adding directories to PYTHONPATH"
export PYTHONPATH=$PYTHONPATH:../greenhouse_controller:web/greenhouse_django_project:../Adafruit-Raspberry-Pi-Python-Code/Adafruit_I2C
echo $PYTHONPATH
echo "running web"
cd web/greenhouse_django_project
python manage.py runserver 10.0.0.3:8000
