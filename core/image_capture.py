import logging
import threading
from datetime import datetime, timedelta
from django.utils import timezone
from time import sleep
import cfg
import utils
import os
import subprocess

__author__ = 'netanel'


class ImageCapture(threading.Thread):
    def __init__(self, save_path, time_between_captures, args_for_raspistill=None):
        super(ImageCapture, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('initializing ImageCapture')
        self.logger.info('save_path: {}'.format(save_path))
        self.logger.info('time_between_captures: {}'.format(time_between_captures))
        self.logger.info('args_for_raspistill: {}'.format(args_for_raspistill))
        self.save_path = save_path
        self.time_between_captures = time_between_captures
        self.args_for_raspistill = args_for_raspistill
        self.last_capture_time = datetime.min
        self.should_run = False
        self.controller_capture_switch = True  # this is meant to be changed from other threads, and allow/ disallow for images to be taken
        utils.register_keep_alive(name=self.__class__.__name__)
        self.logger.info('ImageCapture Finished Init')

    def run(self):
        self.should_run = True
        while self.should_run:
            self.logger.info('image capture thread {}'.format(datetime.now()))
            if self._check_if_should_capture():
                self._capture()
            utils.update_keep_alive(name=self.__class__.__name__)
            sleep(cfg.IMAGE_CAPTURE_WAIT_TIME)

    def change_controller_capture_switch(self, new_state):
        self.logger.debug('in change_controller_capture_switch, new_state: {}'.format(new_state))
        self.controller_capture_switch = new_state

    def _check_if_should_capture(self):
        current_time = datetime.now()
        self.logger.debug('in _check_if_should_capture, current_time: {}, self.last_capture_time: {}, self.time_between_captures: {}'
                          .format(current_time, self.last_capture_time, self.time_between_captures))
        if (current_time - self.last_capture_time > self.time_between_captures) and (self.controller_capture_switch is True):
            return True
        else:
            return False

    def _capture(self):
        self.logger.info('in _capture')
        try:
            filename = 'cap_{}.jpg'.format((timezone.make_naive(value=timezone.now(), timezone=timezone.get_current_timezone()).strftime('%d-%m-%y_%H-%M-%S')))
            file_name = os.path.join(utils.get_root_path(), 'logs', 'pics', filename)
            command = ['raspistill']
            command.extend(self.args_for_raspistill)
            command.extend(['-o', file_name])
            self.logger.debug('built command for subprocess: {}'.format(command))
            subprocess.call(command)
        except Exception as ex:
            self.logger.exception('got exception in capture: {}'.format(ex))
        self.last_capture_time = datetime.now()

    def stop_thread(self):
        self.logger.info('in stop_thread')
        self.should_run = False

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')
    import django
    django.setup()
    utils.init_logging('image_capturer', logging.DEBUG)
    save_path = os.path.join(utils.get_root_path(), 'logs', 'images')
    time_between_captures = timedelta(seconds=120)
    capturer = ImageCapture(save_path=save_path, time_between_captures=time_between_captures, args_for_raspistill=['-vf'])
    capturer.setDaemon(True)
    capturer.start()
    sleep(60*5)
    capturer.stop_thread()
    sleep(11)
