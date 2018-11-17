#! /usr/bin/python

from os.path import expanduser,isfile
import sys
from urllib.request import urlopen
import xml.etree.ElementTree as ElementTree

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

# calculate integrated quantitative precipitation forecast
def precip(forecast_root):
    iqpf = 0
    for qpf_element in forecast_root.iter('hourly-qpf'):
        for qpf in qpf_element.itertext():
            iqpf += bf_number(qpf)
    return iqpf

def main():
    print(precip(get_forecast(get_location_data(sys.argv))))

if __name__ == "__main__":
    main()
