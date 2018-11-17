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

def main():
    forecast = get_forecast(get_location_data(sys.argv))
    print("Precipitation: %.2f inches" %
            sp.sum(get_series(forecast, 'hourly-qpf')))
    temp = get_series(forecast, 'temperature', type_filter='hourly')
    print("max/min: %.0f/%.0f F" % (sp.amax(temp), sp.amin(temp)))
    print("dew point: %.0f F" %
            sp.mean(get_series(forecast, 'temperature', type_filter='dew point')))
    wind_chill = get_series(forecast, 'temperature', type_filter='wind chill')
    print("wind chill: %.0f/%.0f F" % (sp.amax(wind_chill), sp.amin(wind_chill)))

if __name__ == "__main__":
    main()
