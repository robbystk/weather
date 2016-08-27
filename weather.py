#! /usr/bin/python2

from __future__ import print_function
from os.path import expanduser,isfile
import sys
from urllib import urlopen
import xml.etree.ElementTree as ElementTree

location_path="~/.location"

def printerr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def location_from_homedir():
    if isfile(expanduser(location_path)):
        with open(expanduser(location_path)) as f:
            return "&".join(f.read().split("\n"))
    else:
        printerr("no location file at " + location_path)
        sys.exit(2)

def location_from_file(location_file):
    try:
        f = open(expanduser(location_file),'r')
    except:
        printerr("file " + location_file + " not found")
        return location_from_homedir()

# brute-force number from whatever
def bf_number(thing):
    try:
        return float(thing)
    except:
        return 0

if len(sys.argv) == 1:
    # not given location file
    data = location_from_homedir()
elif len(sys.argv) == 2:
    # given location file
    data = location_from_file(sys.argv[1])
else:
    # wrong number of arguments
    printerr("Usage: " + sys.argv[0] + " [location file]")
    sys.exit(1)

url="http://forecast.weather.gov/MapClick.php?"+data+"FcstType=digitalDWML"
forecast = urlopen(url).read()

# parse xml
root = ElementTree.fromstring(forecast)

# calculate integrated probabilistic quantitative precipitation forecast
iqpf = 0
for qpf_element in root.iter('hourly-qpf'):
    for qpf in qpf_element.itertext():
        iqpf += bf_number(qpf)

print(iqpf)
