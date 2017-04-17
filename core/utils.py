__author__ = 'netanel'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')
import django
django.setup()
from django.utils import timezone
from greenhouse_app.models import KeepAlive
import logging
from logging.handlers import RotatingFileHandler


def get_root_path():
    """
    :return: the absolute path of greenhouse_controller from some path within
    """
    dir_to_check = os.getcwd()
    while not os.path.exists(os.path.join(dir_to_check, 'greenhouse_controller')):
        dir_to_check = os.path.join(dir_to_check, '..')

    return os.path.abspath(os.path.join(dir_to_check, 'greenhouse_controller'))


def init_logging(logger_name, logger_level):
    logger = logging.getLogger()
    s_handler = logging.StreamHandler()
    f_handler = RotatingFileHandler(filename=os.path.join(get_root_path(), 'logs', '{}_{}.log'
                                            .format(logger_name, timezone.make_naive(value=timezone.now(),
                                                                                     timezone=timezone.get_current_timezone())
                                                    .strftime('%d-%m-%y_%H-%M-%S'))),
                                    maxBytes=10E6,
                                    backupCount=500)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    s_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)
    logger.addHandler(s_handler)
    logger.addHandler(f_handler)
    logger.setLevel(logger_level)


def register_keep_alive(name):
    """
    ensure keepalive table has a row for brain
    :param name: name of model for registering keepalive
    :return:
    """
    l = logging.getLogger('utils')
    try:
        l.info('trying to add {} into KeepAlive table'.format(name))
        KeepAlive.objects.get_or_create(name=name, timestamp=timezone.now())
    except Exception as ex:
        l.exception('got exception: {}'.format(ex))


def update_keep_alive(name, failure_manager):
    """
    write new timestamp to keepalive table
    :return:
    """
    l = logging.getLogger('utils')
    try:
        t = timezone.now()
        l.debug('trying to update {} KeepAlive timestamp to: {}'.format(name, t))
        k = KeepAlive.objects.get(name=name)
        k.timestamp = t
        k.save()
    except Exception as ex:
        l.exception('got exception: {}'.format(ex))
        failure_manager.add_failure(ex=ex, caller=update_keep_alive.__name__)

