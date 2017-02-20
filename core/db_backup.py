__author__ = 'netanel'
import logging
import threading
from datetime import datetime, timedelta
from time import sleep
import os
import cfg
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greenhouse_django_project.settings')
import django
django.setup()
from greenhouse_app.models import Measure


class DbBackupper(threading.Thread):
    """
    thread that ensures working DB (actually only measures Table in DB) stays small.
    if Measurements table has more than NUMBER_OF_ITEMS_IN_RPI_DB records:
    the thread starts to move the old records chunk by chunk to a backup DB
    """
    def __init__(self):
        super(DbBackupper, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.should_run = False

    def run(self):
        self.should_run = True
        while self.should_run:
            self.logger.info('db backup thread {}'.format(datetime.now()))
            data = self._check_if_should_backup()
            if data is not None:
                self._send_data_to_backup(data)

            sleep(cfg.DB_BACKUPPER_WAIT_TIME)

    def stop_thread(self):
        self.logger.info('in stop_thread')
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


class DbMover(threading.Thread):

    def __init__(self):
        super(DbMover, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.should_run = False
        self.os_name = os.name
        self.last_moving_time = datetime.now() - timedelta(days=365)  # just sometime in the past for intilizing

    def run(self):
        self.should_run = True
        self.logger.info('Starting DbMover {}'.format(datetime.now()))
        while self.should_run:
            if self._check_if_should_move(src=cfg.LOCAL_BACKUP_DB_PATH):
                self._copy_backup_db(src=cfg.LOCAL_BACKUP_DB_PATH, dst=cfg.REMOTE_BACKUP_DB_PATH)

            sleep(cfg.DB_BACKUPPER_WAIT_TIME)

    def _check_if_should_move(self, src):
        try:
            modification_time = os.path.getmtime(src)
            datetime_modification_time = datetime.fromtimestamp(modification_time)
            self.logger.debug('src last modification time: {}, ({})'.format(modification_time, datetime_modification_time))
            if datetime_modification_time > self.last_moving_time:
                self.logger.debug('last moving time: {}, last modification time of backup file: {}, therefor moving to remote'.format(self.last_moving_time, datetime_modification_time))
                return True
            else:
                self.logger.debug('last moving time: {}, last modification time of backup file: {}, doing nothing'.format(self.last_moving_time, datetime_modification_time))
                return False
        except Exception as ex:
            self.logger.error('could not get modification time for src file, ex: {}'.format(ex))

    def _copy_backup_db(self, src, dst):
        self.logger.info('in copy_backup_db')
        self.logger.debug('src: {}'.format(src))
        self.logger.debug('dst: {}'.format(dst))

        try:
            shutil.copy2(src=src, dst=dst)
            self.last_moving_time = datetime.now()
        except Exception as ex:
            self.logger.error('could not get modification time for src file, ex: {}'.format(ex))

    def stop_thread(self):
        self.logger.info('in stop_thread (DbMover)')
        self.should_run = False

if __name__ == '__main__':
    from brain import init_logging
    init_logging()
    mover = DbMover()
    mover.setDaemon(True)
    mover.start()
    sleep(20)
    mover.stop_thread()
    sleep(5)