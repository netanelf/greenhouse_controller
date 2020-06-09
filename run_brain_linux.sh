#!/bin/bash 

echo "adding directories to PYTHONPATH"
export PYTHONPATH=$PYTHONPATH:../greenhouse_controller:web/greenhouse_django_project:../Adafruit-Raspberry-Pi-Python-Code/Adafruit_I2C
echo $PYTHONPATH
echo "running core"
python3 core/brain.py $1
