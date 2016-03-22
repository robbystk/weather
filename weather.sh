#! /usr/bin/python2

from os.path import expanduser,isfile
from sys import argv

url="http://forecast.weather.gov/MapClick.php"
location_path="~/.location"

def location_from_homedir():
    if isfile(expanduser(location_path)):
        with open(expanduser(location_path)) as f:
            data = f.read()
    else:
        print "no location file at " + location_path


def location_from_file(file):
    try:
        f = open(expanduser(file))
    except:
        print "file $location_file not found"
        location_from_homedir

if len(argv) == 1:
    # not given location file
    location_from_homedir()
elif len(argv) == 2:
    # given location file
    location_from_file(argv[1])
else:
    # wrong number of arguments
    print "Usage: $0 [location file]"

# curl -sGd "lat=${lat}&lon=${lon}&FcstType=digital" $url >forecast.html
