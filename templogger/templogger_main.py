#!/usr/bin/env python3

import logging
from time import sleep

from templogger.logger import HTDevicePoller, HTDataBaseHandler
from templogger.utils.device_config_parser import device_config_parser
from templogger.visualiser import HTDataVisualiser

_logger = logging.getLogger('templogger')
_logger.setLevel(level=logging.DEBUG)
_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_sh = logging.StreamHandler()
_sh.setLevel(level=logging.INFO)
_sh.setFormatter(_formatter)
_logger.addHandler(_sh)


def main(host_ip='192.168.100.180', port=8080, write_log_to_file=True):
    if write_log_to_file:
        fh = logging.FileHandler('templogger.log')
        fh.setLevel(level=logging.DEBUG)
        fh.setFormatter(_formatter)
        _logger.addHandler(fh)
    _logger.info('Running script...')
    config = device_config_parser()
    # Data base handler
    db_handler = HTDataBaseHandler()
    # Data poller
    poller = HTDevicePoller(config['General']['device_sample_interval_s'],
                            config['devices'],
                            db_handler)
    # Data visualiser
    visualiser = HTDataVisualiser(config['General']['plot_refresh_interval_s'],
                                  config['devices'],
                                  db_handler,
                                  config['General']['default_hours_view'])
    try:
        poller.start_pollers()
        visualiser.start(host_ip=host_ip, port=port)
        while True:
            sleep(2)
    except KeyboardInterrupt:
        _logger.info('Got keyboard interrupt!')
    finally:
        _logger.info('Stopping script..')
        poller.stop_pollers()
        sleep(config['General']['device_sample_interval_s'] + 5)
        db_handler.close()
    _logger.info('Script finished')


if __name__ == '__main__':
    main()
