__author__ = 'netanel'
import logging
import threading
from datetime import datetime
from time import sleep
import os
import cfg

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')
import django
django.setup()
from greenhouse_app.models import Measure


class DbBackuper(threading.Thread):
    def __init__(self):
        super(DbBackuper, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.should_run = False

    def run(self):
        self.should_run = True
        while self.should_run:
            self.logger.info('db backup thread {}'.format(datetime.now()))
            data = self._check_if_should_backup()
            self._send_data_to_backup(data)

            sleep(cfg.DB_BACKUPPER_WAIT_TIME)

    def stop_thread(self):
        print 'in stop_thread'
        self.should_run = False

    def _check_if_should_backup(self):
        measures = Measure.objects.all()
        length = measures.count()
        self.logger.info('data lenght: {}'.format(length))
        if length > cfg.NUMBER_OF_ITEMS_IN_RPI_DB:
            return Measure.objects.order_by('measure_time')[0:cfg.NUMBER_OF_ITEMS_TO_MOVE_ONCE]

    def _send_data_to_backup(self, data):
        try:
            for d in data:
                if self._write_data_to_backup(one_measure=d):
                    self._delete_data_from_local(d)
        except Exception as ex:
            self.logger.error('while db backup, got exception: {}'.format(ex))

    def _write_data_to_backup(self, one_measure):
        self.logger.debug('writing {} to server backup'.format(one_measure))
        one_measure.save(using='backup')
        return True

    def _delete_data_from_local(self, one_measure):
        self.logger.debug('deleting {} from local db'.format(one_measure))
        one_measure.delete(using='default')

