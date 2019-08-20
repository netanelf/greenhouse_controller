#!/bin/bash

cd /home/pi/workspace/greenhouse_controller/web/greenhouse_django_project
rm -f *.sqlite3

cd /home/pi/workspace/greenhouse_controller/web/greenhouse_django_project/greenhouse_app/migrations
rm -f [0-9]*

cd /home/pi/workspace/greenhouse_controller/web/greenhouse_django_project
python manage.py makemigrations greenhouse_app
python manage.py migrate --database='backup'
python manage.py migrate --database='default'
python populate_greenhouse_app_rpi.py

