#!/usr/bin/env python3

import configparser
import os


def device_config_parser(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'devices.config')
    config_obj = configparser.ConfigParser()
    assert os.path.exists(path)
    config_obj.read(path)

    config = dict()
    config['General'] = config_obj._sections['General']
    config['General']['devices'] = config['General']['devices'].split(',')
    config['General']['plot_refresh_interval_s'] = int(config['General']['plot_refresh_interval_s'])
    config['General']['device_sample_interval_s'] = int(config['General']['device_sample_interval_s'])
    config['General']['default_hours_view'] = int(config['General']['default_hours_view'])
    config['General']['show_current_temp_for_device'] = config['General']['show_current_temp_for_device']

    config['devices'] = dict()
    for dev in config['General']['devices']:
        config['devices'][dev] = config_obj._sections[dev]
        config['devices'][dev]['temp_offset'] = float(config['devices'][dev]['temp_offset'])
        config['devices'][dev]['humid_offset'] = float(config['devices'][dev]['humid_offset'])
    return config
