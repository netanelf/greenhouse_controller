import logging
from datetime import datetime, timedelta
from django.utils import timezone
import core.utils as utils
import os
import subprocess

__author__ = 'netanel'


class ImageCapture(object):
    def __init__(self, save_path, failure_manager=None, args_for_raspistill=[]):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('initializing ImageCapture')
        self._logger.info('save_path: {}'.format(save_path))
        self._logger.info('args_for_raspistill: {}'.format(args_for_raspistill))
        self._save_path = save_path
        self._args_for_raspistill = args_for_raspistill
        self._last_capture_time = datetime.min
        self._should_run = False
        self._failure_manager = failure_manager
        self._logger.info('ImageCapture Finished Init')

    def capture_image_and_save(self, simulate=False):
        self._logger.info('in _capture')

        if simulate:
            filename = 'cap_{}.txt'.format((timezone.make_naive(value=timezone.now(),
                                                                timezone=timezone.get_current_timezone()).strftime(
                '%d-%m-%y_%H-%M-%S')))
            file_name = os.path.join(utils.get_root_path(), 'logs', 'pics', filename)
            with open(file_name, 'w') as f:
                f.write('just a simulated image')
        try:
            filename = 'cap_{}.jpg'.format((timezone.make_naive(value=timezone.now(),
                                                                timezone=timezone.get_current_timezone()).strftime(
                '%d-%m-%y_%H-%M-%S')))
            file_name = os.path.join(utils.get_root_path(), 'logs', 'pics', filename)
            command = ['raspistill']
            command.extend(self._args_for_raspistill)
            command.extend(['-o', file_name])
            self._logger.debug('built command for subprocess: {}'.format(command))
            subprocess.Popen(command)
        except Exception as ex:
            self._logger.exception('got exception in capture: {}'.format(ex))



if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')
    import django
    django.setup()
    utils.init_logging('image_capturer', logging.DEBUG)
    save_path = os.path.join(utils.get_root_path(), 'logs', 'images')
    time_between_captures = timedelta(seconds=120)
    RASPISTILL_ARGS = ['-a', '12']
    capturer = ImageCapture(save_path=save_path, args_for_raspistill=RASPISTILL_ARGS)
    capturer.capture_image_and_save()

