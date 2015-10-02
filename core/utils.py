__author__ = 'netanel'

import os


def get_root_path():
    """
    :return: the absolute path of greenhouse_controller from some path within
    """
    dir_to_check = os.getcwd()
    while not os.path.exists(os.path.join(dir_to_check, 'greenhouse_controller')):
        dir_to_check = os.path.join(dir_to_check, '..')

    return os.path.abspath(os.path.join(dir_to_check, 'greenhouse_controller'))


