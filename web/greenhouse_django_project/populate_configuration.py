import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')

import django
django.setup()

from greenhouse_app.models import ConfigurationInt, ConfigurationStr

if __name__ == '__main__':
    print('Starting population script...')
    dbs = ['default']
    for db in dbs:
        print(f'starting DB: {db}')

        c = ConfigurationInt.objects.using(db).get_or_create(name='manual_mode')[0]
        c.value = 0
        c.explanation = 'if set to 1, governors do not change relay states, only manual user changes'
        c.save(using=db)

        c = ConfigurationStr.objects.using(db).get_or_create(name='sendgrid_api_key')[0]
        c.value = ''
        c.explanation = 'Your SendGrid API key, to be used with Email actions'
        c.save(using=db)

        c = ConfigurationStr.objects.using(db).get_or_create(name='sendgrid_sender_address')[0]
        c.value = ''
        c.explanation = 'The SendGrid sender you want to be used (configured in SendGrid)'
        c.save(using=db)
