#!/usr/bin/env python3

from time import sleep
from threading import Thread, Lock, Event
from datetime import datetime

import btlewrap
from btlewrap.bluepy import BluepyBackend
from mitemp_bt.mitemp_bt_poller import MiTempBtPoller, MI_TEMPERATURE, MI_HUMIDITY


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
            t = Thread(target=self.poll_device_thread, args=(self.poll_interval, self._cancel_event, device, poller,
                                                             self.__bluetooth_access_lock, self.database_handler))
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
                try:
                    mitemp_poller.fill_cache()
                except btlewrap.base.BluetoothBackendException:
                    print('Got error getting reading from', device)
                    continue
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
