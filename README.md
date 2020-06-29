# Templogger
> Logging and plotting of temperature

Python module for logging temperature and humidity from Xiaomi Humidity and Temperature sensors to an SQLite databise 
while continuously plotting the data using a Dash server. 
Works perfectly on a Raspberry Pi.

## Components
The module consist of two submodules:
1. `logger` module, containing:
    - A `HTDevicePoller` class for sampling the HT devices
    - A `HTDataBaseHandler` class for accessing the SQLite database
2. A `visualiser` module containing the `HTDataVisualiser` class for hosting a local Dash server for visualising the logged data.

The `HTDevicePoller` creates a thread per HT device for connecting and reading out samples of humidity and temperature 
with the given interval. 
When a sample is obtained, it is written to `HTDataBaseHandler`, which handles serialising 
access to the database.
`HTDataVisualiser` starts the Dash-server, which with a given interval updates a plot with the historic samples.
In the `templogger_main.py`, an example of how to setup instances of the modules are given, 
using the contained `devices.config`-file that can be read with the config-parser provided in `utils`.

## Authors

* **Mathias Rønholt Kielgast** - *Initial work and development* - [MKielg11](https://github.com/mkielg11)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Thanks to [ratcashdev](https://github.com/ratcashdev) for providing a driver for the Xiaomi sensors (mitemp).

