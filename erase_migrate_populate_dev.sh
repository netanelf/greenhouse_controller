#!/bin/bash

cd web/greenhouse_django_project/
rm -f *.sqlite3

cd greenhouse_app/migrations/
rm -f [0-9]*

cd ../..
python3 manage.py makemigrations greenhouse_app
python3 manage.py migrate --database='backup'
python3 manage.py migrate --database='default'
python3 populate_greenhouse_app.py

echo "from django.contrib.auth.models import User; User.objects.create_superuser('user', 'admin@example.com', 'user')" | python3 manage.py shell
