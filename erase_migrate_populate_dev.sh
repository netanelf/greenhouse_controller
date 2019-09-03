#!/bin/bash

cd web/greenhouse_django_project/
rm -f *.sqlite3

cd greenhouse_app/migrations/
rm -f [0-9]*

cd ../..
python manage.py makemigrations greenhouse_app
python manage.py migrate --database='backup'
python manage.py migrate --database='default'
python populate_greenhouse_app.py

echo "from django.contrib.auth.models import User; User.objects.create_superuser('netanel', 'admin@example.com', 'netanel')" | python manage.py shell
