#! /usr/bin/python

from os.path import expanduser,isfile
import sys
from urllib.request import urlopen
import xml.etree.ElementTree as ElementTree
import scipy as sp
import matplotlib.pyplot as plt

location_path="~/.location"

def printerr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def location_data_from_homedir():
    if isfile(expanduser(location_path)):
        with open(expanduser(location_path)) as f:
            return "&".join(f.read().split("\n"))
    else:
        printerr("no location file at " + location_path)
        return None

def location_data_from_file(location_file):
    try:
        f = open(expanduser(location_file),'r')
    except:
        printerr("file " + location_file + " not found")
        return None

def get_location_data(args):
    if len(args) == 1:
        # not given location file
        data = location_data_from_homedir()
    elif len(args) == 2:
        # given location file
        data = location_data_from_file(args[1])
        if data == None:
            data = location_data_from_homedir()
    else:
        # wrong number of arguments
        printerr("Usage: " + args[0] + " [location file]")
        sys.exit(1)

    if data == None:
        printerr("Could not get location data")
        sys.exit(2)
    else:
        return data

# brute-force number from whatever
def bf_number(thing):
    try:
        return float(thing)
    except:
        return 0

def get_forecast(data):
    url="http://forecast.weather.gov/MapClick.php?"+data+"FcstType=digitalDWML"
    forecast = urlopen(url).read()

    # parse xml
    root = ElementTree.fromstring(forecast)
    return root

def get_series(forecast_root, variable, type_filter=None, transform=float):
    def get_array(series, transform):
        return sp.array([transform(point) for point in series.itertext()])

    series_array = list(forecast_root.iter(variable))
    if len(series_array) == 1 or type_filter == None:
        return get_array(series_array[0], transform)
    else:
        for series in series_array:
            if series.attrib['type'] == type_filter:
                return get_array(series, transform)

def rms(A):
    return sp.sqrt(sp.mean(A**2))

class wind:
    def __init__(self, speed, direction):
        self.speed = speed
        self.direction = direction

    @property
    def ns_comp(self):
        return self.speed * sp.cos(self.direction * sp.pi / 180)

    @property
    def ew_comp(self):
        return self.speed * sp.sin(self.direction * sp.pi / 180)

    def mean_direction(self):
        mean_ns = sp.mean(self.ns_comp)
        mean_ew = sp.mean(self.ew_comp)
        angle = sp.arctan2(mean_ew, mean_ns) * 180 / sp.pi
        return angle

def deg2str(angle):
    # octant = sp.around(angle / 360 * 8) % 8
    dodecant = sp.around(angle / 360 * 16) % 16
    # dirs = {0: 'N', 1: 'NE', 2: 'E', 3: 'SE', 4: 'S', 5: 'SW', 6: 'W', 7: 'NW'}
    dirs = {0: 'N', 1: 'NNE', 2: 'NE', 3: 'ENE',
            4: 'E', 5: 'ESE', 6: 'SE', 7: 'SSE',
            8: 'S', 9: 'SSW', 10: 'SW', 11: 'WSW',
            12: 'W', 13: 'WNW', 14: 'NW', 15: 'NNW'}
    return dirs[dodecant]

def get_wind(forecast_root):
    wind_speed = get_series(forecast_root, 'wind-speed')
    wind_direction = get_series(forecast_root, 'direction')
    return wind(wind_speed, wind_direction)

def plot_wind(forecast_root):
    wind = get_wind(forecast_root)
    wind_NS = wind.speed * sp.cos(wind.direction * sp.pi / 180)
    wind_EW = wind.speed * sp.sin(wind.direction * sp.pi / 180)

    max_speed = sp.amax(wind.speed)

    plt.plot(wind_EW[:49], wind_NS[:49])
    plt.axis([-max_speed, max_speed, -max_speed, max_speed])
    plt.xlabel('East/West')
    plt.ylabel('North/South')
    plt.show()

def main():
    forecast = get_forecast(get_location_data(sys.argv))
    print("Precipitation: %.2f inches" %
            sp.sum(get_series(forecast, 'hourly-qpf')))
    wind = get_wind(forecast)
    print("Wind speed: %.2f mph" % rms(wind.speed))
    print("Average wind direction: %s" % deg2str(wind.mean_direction()))
    temp = get_series(forecast, 'temperature', type_filter='hourly')
    print("max/min: %.0f/%.0f F" % (sp.amax(temp), sp.amin(temp)))
    print("dew point: %.0f F" %
            sp.mean(get_series(forecast, 'temperature', type_filter='dew point')))
    wind_chill = get_series(forecast, 'temperature', type_filter='wind chill')
    print("wind chill: %.0f/%.0f F" % (sp.amax(wind_chill), sp.amin(wind_chill)))

    plot_wind(forecast)

if __name__ == "__main__":
    main()
