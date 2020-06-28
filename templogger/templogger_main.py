#!/usr/bin/env python3

import os
import configparser
from time import sleep

from templogger.logger import HTDevicePoller, HTDataBaseHandler


def device_config_parser(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'devices.config')
    config_obj = configparser.ConfigParser()
    assert os.path.exists(path)
    config_obj.read(path)

    config = dict()
    config['General'] = config_obj._sections['General']
    config['General']['devices'] = config['General']['devices'].split(',')
    config['General']['plot_refresh_interval_s'] = int(config['General']['plot_refresh_interval_s'])
    config['General']['device_sample_interval_s'] = int(config['General']['device_sample_interval_s'])

    config['devices'] = dict()
    for dev in config['General']['devices']:
        config['devices'][dev] = config_obj._sections[dev]
        config['devices'][dev]['temp_offset'] = float(config['devices'][dev]['temp_offset'])
    return config


def main():
    print('Running script...')
    config = device_config_parser()
    print('Got config:', config)
    db_handler = HTDataBaseHandler()
    poller = HTDevicePoller(config['General']['device_sample_interval_s'], config['devices'], db_handler)
    poller.start_pollers()
    try:
        while True:
            sleep(2)
    except KeyboardInterrupt:
        print('Stopping script..')
        poller.stop_pollers()
        sleep(config['General']['device_sample_interval_s'] + 5)
        db_handler.close()
    print('Script finished')


if __name__ == '__main__':
    main()
