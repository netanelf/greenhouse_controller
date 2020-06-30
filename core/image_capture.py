import logging
import threading
from datetime import datetime, timedelta
from django.utils import timezone
from time import sleep
import cfg
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

    # def run(self):
    #     self.should_run = True
    #     while self.should_run:
    #         try:
    #             self.logger.info('image capture thread {}'.format(datetime.now()))
    #             if self._check_if_should_capture():
    #                 self._capture()
    #             utils.update_keep_alive(name=self.__class__.__name__, failure_manager=self.failure_manager)
    #             sleep(cfg.IMAGE_CAPTURE_WAIT_TIME)
    #         except Exception as ex:
    #             self.logger.exception(ex)

    # def change_controller_capture_switch(self, new_state):
    #     self.logger.debug('in change_controller_capture_switch, new_state: {}'.format(new_state))
    #     self.controller_capture_switch = new_state
    #
    # def _check_if_should_capture(self):
    #     current_time = datetime.now()
    #     self.logger.debug('in _check_if_should_capture, current_time: {}, self.last_capture_time: {}, self.time_between_captures: {}'
    #                       .format(current_time, self.last_capture_time, self.time_between_captures))
    #     if (current_time - self.last_capture_time > self.time_between_captures) and (self.controller_capture_switch is True):
    #         return True
    #     else:
    #         return False

    def capture_image_and_save(self):
        self._logger.info('in _capture')
        try:
            filename = 'cap_{}.jpg'.format((timezone.make_naive(value=timezone.now(), timezone=timezone.get_current_timezone()).strftime('%d-%m-%y_%H-%M-%S')))
            file_name = os.path.join(utils.get_root_path(), 'logs', 'pics', filename)
            command = ['raspistill']
            command.extend(self._args_for_raspistill)
            command.extend(['-o', file_name])
            self._logger.debug('built command for subprocess: {}'.format(command))
            #subprocess.call(command)
            subprocess.Popen(command)
        except Exception as ex:
            self._logger.exception('got exception in capture: {}'.format(ex))
        self.last_capture_time = datetime.now()

    # def stop_thread(self):
    #     self.logger.info('in stop_thread')
    #     self.should_run = False


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

