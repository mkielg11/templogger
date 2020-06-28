#!/usr/bin/env python3
import socket
from datetime import datetime, timedelta
from threading import Event

import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


class HTDataVisualiser:
    _app = dash.Dash('HTDataVisualiser')

    def __init__(self, plot_interval, device_config, database_handler, default_hours_view=48):
        self.plot_interval = plot_interval
        self.default_hours_view = default_hours_view
        self.database_handler = database_handler
        self._device_config = device_config
        self._cancel_event = Event()

    def start(self, host_ip=None, port=8080, debug=False):
        self._app.layout = html.Div(
            html.Div([
                # html.H4('Temperature over time'),
                dcc.Graph(
                    id='live-update-graph',
                    animate=True,
                ),
                dcc.Interval(
                    id='interval-component',
                    interval=self.plot_interval * 1000,  # in milliseconds
                    n_intervals=0
                )
            ])
        )

        @self._app.callback(Output('live-update-graph', 'figure'),
                            [Input('interval-component', 'n_intervals')])
        def update_visualise(n):
            return self.visualise(n)

        # self.visualise(self.plot_interval, self._device_config, self.database_handler)
        if host_ip is None:
            hostname = socket.gethostname()
            host_ip = socket.gethostbyname(hostname)
        self._app.run_server(debug=debug, port=port, host=host_ip)

    def visualise(self, n):
        data = self.database_handler.get_data()
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.update_layout(
            title='Temperature and humidity over time',
            xaxis_title='Date and time',
        )

        fig.update_yaxes(title_text='Temperature (Celsius)', secondary_y=False)
        fig.update_yaxes(title_text='Humidity [dashed] (%)', secondary_y=True)
        for device, device_setting in self._device_config.items():
            device_data = data[data.device == device]
            device_data = device_data.set_index(pd.DatetimeIndex(device_data['date']))
            device_mean_temp_per_min = (device_data.groupby(pd.Grouper(freq='min')).temperature.mean()
                                        - device_setting['temp_offset'])
            device_mean_humid_per_min = (device_data.groupby(pd.Grouper(freq='min')).humidity.mean()
                                         - device_setting['humid_offset'])

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
        default_xaxis_min = datetime.now() - timedelta(hours=self.default_hours_view)
        if data.date.min() < default_xaxis_min:
            fig.update_layout(xaxis={range: [default_xaxis_min, datetime.now()]})
        return fig


if __name__ == '__main__':
    from templogger.templogger_main import device_config_parser
    from templogger.logger import HTDataBaseHandler
    config = device_config_parser()
    db_handler = HTDataBaseHandler()
    # poller = HTDevicePoller(config['General']['device_sample_interval_s'], config['devices'], db_handler)

    data_visualiser = HTDataVisualiser(config['General']['plot_refresh_interval_s'], config['devices'], db_handler)
    data_visualiser.start()
