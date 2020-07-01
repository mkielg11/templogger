#!/usr/bin/env python3

import socket
from datetime import datetime, timedelta
from threading import Event
from collections import OrderedDict

import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output


class HTDataVisualiser:
    _app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css', ])

    def __init__(self, plot_interval, device_config, database_handler, default_hours_view=48):
        self.plot_interval = plot_interval
        self.default_hours_view = default_hours_view
        self.database_handler = database_handler
        self._fig = make_subplots(specs=[[{"secondary_y": True}]])
        self._device_config = OrderedDict(device_config)
        self._cancel_event = Event()

    def start(self, host_ip=None, port=8080, debug=False):
        thermometer_obj_list = list()
        div_list = [
            html.H1('TempLogger Dash'),
            dcc.Graph(
                id='live-update-graph',
                animate=True,
            ),
            dcc.Interval(
                id='interval-component',
                interval=self.plot_interval * 1000,  # in milliseconds
                n_intervals=0
            ),
        ]
        callback_output_list = [Output('live-update-graph', 'figure'), ]
        for device in self._device_config:
            th_id = '{}-thermometer'.format(device.lower())
            callback_output_list.append(Output(th_id, 'value'))
            thermometer_obj_list.append(daq.Thermometer(
                id=th_id,
                value=20,
                min=0,
                max=35,
                style={
                    'margin-bottom': '5%',
                    'width': '25%',
                    'display': 'inline-block',
                    'textAlign': 'center'
                },
                showCurrentValue=True,
                units="C",
                label='Current temperature, {}'
                    .format(self._device_config[device]['location'].capitalize()),
                labelPosition='top'
            ))
        div_list.append(html.Div(thermometer_obj_list, style={'textAlign': 'center'}))
        self._app.layout = html.Div(
            html.Div(div_list)
        )

        @self._app.callback(callback_output_list,
                            [Input('interval-component', 'n_intervals')])
        def update_visualise(n):
            return self.visualise(n)

        if host_ip is None:
            hostname = socket.gethostname()
            host_ip = socket.gethostbyname(hostname)
        self._app.run_server(debug=debug, port=port, host=host_ip)

    def visualise(self, n):
        data = self.database_handler.get_data()
        if not n:
            self._fig.update_layout(
                title='Temperature and humidity over time',
                xaxis_title='Date and time',
            )
            self._fig.update_yaxes(title_text='Temperature (Celsius)', secondary_y=False)
            self._fig.update_yaxes(title_text='Humidity [dashed] (%)', secondary_y=True)
        
        self._fig.data = list()  # Make sure fig is empty
        current_temps = list()
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
                name=device_setting['location'].capitalize(),
                line={
                    'color': device_setting['identifier'],
                }
            )
            dev_humid_plot = go.Scatter(
                x=device_mean_humid_per_min.index,
                y=device_mean_humid_per_min.values,
                mode='lines',
                name=device_setting['location'].capitalize(),
                line={
                    'color': device_setting['identifier'],
                    'dash': 'dash'
                },
                showlegend=False
            )
            self._fig.add_trace(dev_temp_plot, secondary_y=False)
            self._fig.add_trace(dev_humid_plot, secondary_y=True)
            current_temps.append(device_data.iloc[-1].temperature)
        default_xaxis_min = datetime.now() - timedelta(hours=self.default_hours_view)
        if not n and (data.date.min() < default_xaxis_min):
            self._fig.update_layout(xaxis={'range': [default_xaxis_min, datetime.now()]})
        return (self._fig, *current_temps)


if __name__ == '__main__':
    from templogger.utils.device_config_parser import device_config_parser
    from templogger.logger import HTDataBaseHandler

    config = device_config_parser()
    db_handler = HTDataBaseHandler()

    data_visualiser = HTDataVisualiser(config['General']['plot_refresh_interval_s'],
                                       config['devices'],
                                       db_handler,
                                       config['General']['default_hours_view'])
    data_visualiser.start(debug=True)
