
from threading import Thread, Timer

from mitemp_bt.mitemp_bt_poller import MiTempBtPoller
from btlewrap.bluepy import BluepyBackend


class HTDevicePoller:
    def __init__(self, poll_interval, device_config):
        self.poll_interval = poll_interval
        self._device_config = device_config
        self.__threads = dict()

    def start_pollers(self):
        for device, device_config in self._device_config.items():
            poller = MiTempBtPoller(device_config['mac'], BluepyBackend, cache_timeout=self.poll_interval)
            t = Timer(self.poll_interval, self.poll_interval, args=(device, poller, )).start()
            self.__threads[device] = t

    def stop_pollers(self):
        for device in self._device_config:
            self.__threads[device].cancel()

    @staticmethod
    def poll_device(device, mitemp_poller):
        mitemp_poller.fill_cache()
        print(device, mitemp_poller.parameter_value("temperature"))
