#! /usr/bin/python2

from os.path import expanduser,isfile
import sys
from urllib import urlopen

location_path="~/.location"

def location_from_homedir():
    if isfile(expanduser(location_path)):
        with open(expanduser(location_path)) as f:
            return "&".join(f.read().split("\n"))
    else:
        print "no location file at " + location_path
        sys.exit(2)

def location_from_file(location_file):
    try:
        f = open(expanduser(location_file),'r')
    except:
        print "file " + location_file + " not found"
        return location_from_homedir()

if len(sys.argv) == 1:
    # not given location file
    data = location_from_homedir()
elif len(sys.argv) == 2:
    # given location file
    data = location_from_file(sys.argv[1])
else:
    # wrong number of arguments
    print "Usage: " + sys.argv[0] + " [location file]"
    sys.exit(1)

url="http://forecast.weather.gov/MapClick.php?"+data+"FcstType=digitalDWML"
forecast = urlopen(url).read()
