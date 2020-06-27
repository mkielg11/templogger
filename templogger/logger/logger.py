#!/usr/bin/env python3

import os
import sqlite3
from time import sleep
from threading import Thread, Timer, Lock, Event
from datetime import datetime

from mitemp_bt.mitemp_bt_poller import MiTempBtPoller, MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY
from btlewrap.bluepy import BluepyBackend


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class HTDataBaseHandler:
    TABLE_NAME = 'HT_DATA'
    TABLE_COLUMNS = (('device', 'text'),
                     ('date', 'text'),
                     ('temerature decigrades', 'integer'),
                     ('humidity promille', 'integer'),
                     ('battery status', 'integer'))
    
    def __init__(self, path='ht_data.db'):
        self._db_access_lock = Lock()
        with self._db_access_lock:
            self.db_exists = os.path.exists(path)
            self.db_connection = sqlite3.connect(path, check_same_thread=False)
        
        if not self.db_exists:
            self._init_database()
        
            
    def close(self):
        if self.db_connection:
            self.db_connection.close()
            
    def __del__(self):
        self.close()
        
    def _init_database(self):
        with self._db_access_lock:
            c = self.db_connection.cursor()

            # Create table
            column_definitions = ','.join([' '.join(column) for column in self.TABLE_COLUMNS])
            c.execute('CREATE TABLE {} ({})'.format(self.TABLE_NAME, column_definitions))

            # Save (commit) the changes
            self.db_connection.commit()
        self.db_exists = True
        
    def write_row(self, device, date, temperature, humidity, battery_status):
        if not self.db_exists:
            self._init_database()
        with self._db_access_lock:
            
            c = self.db_connection.cursor()
            c.execute("INSERT INTO {} VALUES ('{}','{}',{},{},{})"
                      .format(self.TABLE_NAME, device, date.strftime(DATETIME_FORMAT),
                              int(round(temperature*10)), int(round(humidity*10)), battery_status))
            
            self.db_connection.commit()
            
    def clean_database(self):
        with self._db_access_lock:
            # Get a cursor object
            cursor = self.db_connection.cursor()
            
            # Execute the DROP Table SQL statement
            cursor.execute('DROP TABLE ' + self.TABLE_NAME)
            self.db_connection.commit()

        self.db_exists = False
        self._init_database()
          

class HTDevicePoller:
    def __init__(self, poll_interval, device_config, database_handler):
        self.poll_interval = poll_interval
        self.database_handler = database_handler
        self._device_config = device_config
        self.__threads = dict()
        self.__bluetooth_access_lock = Lock()
        self._cancel_event = Event()

    def start_pollers(self):
        no_of_devices = len(self._device_config)
        for device, device_config in self._device_config.items():
            poller = MiTempBtPoller(device_config['mac'], BluepyBackend)
            t = Thread(target=self.poll_device_thread, args=(self.poll_interval, self._cancel_event, device, poller, self.__bluetooth_access_lock, self.database_handler))
            t.start()
            self.__threads[device] = t
            sleep(self.poll_interval/no_of_devices)

    def stop_pollers(self):
        self._cancel_event.set()

    @staticmethod
    def poll_device_thread(interval, cancel_event, device, mitemp_poller, lock, db_handler):
        ticker = Event()
        while not ticker.wait(interval) and not cancel_event.is_set():
            with lock:
                mitemp_poller.fill_cache()
                sample_time = datetime.now()
                battery = mitemp_poller.battery_level()
                
            temp = mitemp_poller.parameter_value(MI_TEMPERATURE)
            humid = mitemp_poller.parameter_value(MI_HUMIDITY)
            print(sample_time,
                  device,
                  temp,
                  humid,
                  battery)
            db_handler.write_row(device, sample_time, temp, humid, battery)


if __name__ == '__main__':
    db_handler = HTDataBaseHandler()
    db_handler.clean_database()
    db_handler.write_row('HT_TEST', datetime.now(), 25.4, 51.0, 99)
