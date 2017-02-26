__author__ = 'netanel'

import os
from django.utils import timezone
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


