__author__ = 'netanel'
import logging
import threading
from datetime import datetime, timedelta
from time import sleep
import os
import cfg
import utils

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')
import django
django.setup()
from django.utils import timezone
from greenhouse_app.models import HistoryValue


class DbBackupper(threading.Thread):
    """
    thread that ensures working DB (actually only measures Table in DB) stays small.
    if Measurements table has more than NUMBER_OF_ITEMS_IN_RPI_DB records:
    the thread starts to move the old records chunk by chunk to a backup DB
    """
    def __init__(self, failure_manager):
        super(DbBackupper, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('initializing DbBackupper')
        utils.register_keep_alive(name=self.__class__.__name__)
        self.should_run = False
        self.last_keep_alive_time = timezone.now()
        self.failure_manager = failure_manager

    def run(self):
        self.should_run = True
        while self.should_run:
            self.logger.debug('db backup thread {}'.format(datetime.now()))
            data = self._check_if_should_backup()
            if data is not None:
                self._send_data_to_backup(data)

            if timezone.now() - self.last_keep_alive_time > timedelta(seconds=cfg.KEEP_ALIVE_RESOLUTION):
                self.last_keep_alive_time = timezone.now()
                utils.update_keep_alive(name=self.__class__.__name__, failure_manager=self.failure_manager)

            sleep(cfg.DB_BACKUPPER_WAIT_TIME)

    def stop_thread(self):
        self.logger.info('in stop_thread')
        self.should_run = False

    def _check_if_should_backup(self):
        measures = HistoryValue.objects.all()
        length = measures.count()
        self.logger.info('data lenght: {}'.format(length))
        if length > cfg.NUMBER_OF_ITEMS_IN_RPI_DB:
            return HistoryValue.objects.order_by('measure_time')[0:cfg.NUMBER_OF_ITEMS_TO_MOVE_ONCE]

    def _send_data_to_backup(self, data):
        try:
            for d in data:
                if self._write_data_to_backup(one_measure=d):
                    self._delete_data_from_local(d)
        except Exception as ex:
            self.logger.exception('while db backup, got exception: {}'.format(ex))

    def _write_data_to_backup(self, one_measure):
        self.logger.debug('writing {} to server backup'.format(one_measure))
        one_measure.save(using='backup')
        return True

    def _delete_data_from_local(self, one_measure):
        self.logger.debug('deleting {} from local db'.format(one_measure))
        one_measure.delete(using='default')


if __name__ == '__main__':
    '''
    init_logging()
    mover = DbMover()
    mover.setDaemon(True)
    mover.start()
    sleep(20)
    mover.stop_thread()
    sleep(5)
    '''