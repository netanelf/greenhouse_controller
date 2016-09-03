__author__ = 'netanel'
import os
import time
import logging

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

BASE_DIR = '/sys/bus/w1/devices/'
TIMEOUT = 5


def read_temp_raw(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()
        return lines


def read_ds18b20_temp(sensor_id):
    logger = logging.getLogger('ds18b20_driver')
    sensor_output_file = os.path.join(BASE_DIR, sensor_id, 'w1_slave')
    try:
        lines = read_temp_raw(file_name=sensor_output_file)
        t0 = tc = time.time()
        while lines[0].strip()[-3:] != 'YES' and tc - t0 < TIMEOUT:
            time.sleep(0.2)
            lines = read_temp_raw()
            tc = time.time()

        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
    except Exception as ex:
        logger.error('while trying to read value for sensor: {}, got exception: {}'.format(sensor_id, ex))
        return None

