cd web\greenhouse_django_project
del /q *.sqlite3

cd greenhouse_app
rd /q /s migrations
cd ..

python manage.py makemigrations greenhouse_app
python manage.py migrate --database="backup"
python manage.py migrate --database="default"
python populate_configuration.py
python manage.py shell --command="from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'password')"

pause
