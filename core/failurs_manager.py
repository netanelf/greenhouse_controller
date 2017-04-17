import logging
import threading
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from time import sleep
import cfg

__author__ = 'netanel'


class FailureManager(threading.Thread):
    def __init__(self):
        super(FailureManager, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('initializing FailureManager')
        self.should_run = False
        self.failures = {}
        self.statistics = defaultdict(int)
        self.last_statistics_print_time = datetime.min

    def run(self):
        self.should_run = True
        while self.should_run:
            # if its time, print statistics
            if datetime.now() - self.last_statistics_print_time > cfg.STATISTICS_PRINTING_FREQUENCY:
                self.print_statistics()
                self.last_statistics_print_time = datetime.now()

            # if some failure happens to much times/ frequency, do something
            self.inspect_failures()
            sleep(cfg.FAILURE_MANAGER_WAIT_TIME)

    def stop_thread(self):
        self.logger.info('in stop_thread')
        self.should_run = False

    def inspect_failures(self):
        self.logger.debug('in inspect_failures')
        t_now = datetime.now()
        valid_failures = [k for k in self.failures.keys() if t_now - k < cfg.FAILURE_INSPECTION_TIME]
        partial_statistics = defaultdict(int)
        for k in valid_failures:
            v = self.failures[k]
            key = '{}'.format(v['exception'])
            partial_statistics[key] += 1

        # self.logger.info('inspection histogram:')
        # for k, v in partial_statistics.items():
        #     self.logger.info('  {}: {}'.format(k, v))

        for exception_name, exception_parameters in cfg.FAILURE_EXCEPTIONS_CONFIG.items():

            if exception_name in partial_statistics.keys() and partial_statistics[exception_name] > exception_parameters['times']:
                self.logger.error('"{}" is in failures, amount: {}, allowed amount: {}'
                                  .format(exception_name, partial_statistics[exception_name], exception_parameters['times']))
                if exception_parameters['result'] == 'restart':
                    self.restart_computer()

    def print_statistics(self):
        """
        print statistics of how much times every exception happened
        :return:
        """
        self.logger.info('failures statistics:')
        for k, v in self.statistics.items():
            self.logger.info('  {}: {}'.format(k, v))

    def add_failure(self, ex, caller):
        """
        add some failure to the manager
        :param ex: the exception object that happened and we want to mange it
        :param caller: String, name of thread/ function that adds this exception
        :return:
        """
        self.logger.info('in add_failure')
        str_ex = str(ex)
        self.failures[datetime.now()] = {'exception': str_ex, 'caller': caller}
        self.statistics[str_ex] += 1
        self.logger.info('added failure ({}, {})'.format(ex, caller))

    def restart_computer(self):
        """
        this function should send a restart command to the Rpi/ computer the program is running on
        :return:
        """
        self.logger.info('in restart_computer')
        command = ['sudo', 'restart']
        self.logger.info('created command for subprocess: {}'.format(command))
        subprocess.call(command)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logging.info('1')
    t = FailureManager()
    t.setDaemon(True)
    t.start()
    sleep(2)
    t.restart_computer()
    sleep(5)