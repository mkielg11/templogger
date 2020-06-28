#!/usr/bin/env python3

from threading import Thread, Event

import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots


class HTDataVisualiser:
    def __init__(self, plot_interval, device_config, database_handler):
        self.plot_interval = plot_interval
        self.database_handler = database_handler
        self._device_config = device_config
        self._thread = None
        self._cancel_event = Event()

    def start(self):
        self.visualise(self.plot_interval, self._device_config, self.database_handler)

    @staticmethod
    def visualise(plot_interval, device_config, database_handler):
        data = database_handler.get_data()

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.update_layout(
            title='Temperature over time',
            xaxis_title='Date',
            # xaxis={range: [start, end]},
        )
        fig.update_yaxes(title_text='Temperature (Celsius)', secondary_y=False)
        fig.update_yaxes(title_text='Humidity [dashed] (%)', secondary_y=True)
        for device, device_setting in device_config.items():
            device_data = data[data.device == device]
            device_data = device_data.set_index(pd.DatetimeIndex(device_data['date']))
            device_mean_temp_per_min = (device_data.groupby(pd.Grouper(freq='min')).temperature.mean()
                                        - device_setting['temp_offset'])
            device_mean_humid_per_min = device_data.groupby(pd.Grouper(freq='min')).humidity.mean()

            dev_temp_plot = go.Scatter(
                x=device_mean_temp_per_min.index,
                y=device_mean_temp_per_min.values,
                mode='lines',
                name=device_setting['location'],
                line={
                    'color': device_setting['identifier'],
                }
            )
            dev_humid_plot = go.Scatter(
                x=device_mean_humid_per_min.index,
                y=device_mean_humid_per_min.values,
                mode='lines',
                name=device_setting['location'],
                line={
                    'color': device_setting['identifier'],
                    'dash': 'dash'
                },
                showlegend=False
            )
            fig.add_trace(dev_temp_plot, secondary_y=False)
            fig.add_trace(dev_humid_plot, secondary_y=True)
        fig.show()


if __name__ == '__main__':
    from templogger.templogger_main import device_config_parser
    from templogger.logger import HTDataBaseHandler
    config = device_config_parser()
    db_handler = HTDataBaseHandler()
    # poller = HTDevicePoller(config['General']['device_sample_interval_s'], config['devices'], db_handler)

    data_visualiser = HTDataVisualiser(config['General']['plot_refresh_interval_s'], config['devices'], db_handler)
    data_visualiser.start()
