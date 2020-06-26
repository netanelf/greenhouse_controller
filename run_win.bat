set PYTHONPATH=..\greenhouse_controller;web\greenhouse_django_project

start "Brain" python core\brain.py simulate

cd web\greenhouse_django_project

start "Web" python manage.py runserver 0.0.0.0:8000
