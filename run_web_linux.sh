#!/bin/bash 

echo "adding directories to PYTHONPATH"
export PYTHONPATH=$PYTHONPATH:../greenhouse_controller:web/greenhouse_django_project
echo $PYTHONPATH
echo "running web"
cd web/greenhouse_django_project
python manage.py runserver 10.0.0.3:8000
