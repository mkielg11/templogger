
import configparser

from templogger.logger import HTDevicePoller


def device_config_parser(path='devices.config'):
    config_obj = configparser.ConfigParser()
    config_obj.read(path)

    config = dict()
    config['General'] = config_obj._sections['General']
    config['General']['devices'] = config['General']['devices'].split(',')

    config['devices'] = dict()
    for dev in config['General']['devices']:
        config['devices'][dev] = config_obj._sections[dev]
    return config


if __name__ == '__main__':
    config = device_config_parser()
    HTDevicePoller(config['General']['device_sample_interval_s'], config['devices'])
