#!/usr/bin/python

import json
import sys
import geopy
from geopy.geocoders import Nominatim
import re

def main():

    geolocator = Nominatim()

    json_bars = '../processed/bars_nb.json'
    bar_dict = json.loads(open(json_bars).read())

    bar_reviews = {}
    search = "San Francisco, CA"
    timeout = 60

    s = re.search("(.*)" + search, bar_dict['/biz/scomas-restaurant-san-francisco-3']['bar_address'])
    address = s.group(1) + search
    try:
        location = geolocator.geocode(address, timeout = timeout)
    except AttributeError:
        print 'Address not valid.'


    if False:
        for key in bar_dict:
            s = re.search("(.*)" + search, bar_dict[key]['bar_address'])
            address = s.group(1) + search
            try:
                location = geolocator.geocode(address, timeout = timeout)
            except AttributeError:
                print 'Address not valid.'
#            sys.stdout.write('Address not valid.  Removing %s\n' % bar_dict[key]['bar_name'])
#            del bar_dict[key]
            else:
                print address
                print (location.latitude, location.longitude)
                bar_dict[key]['lat'] = location.latitude
                bar_dict[key]['long'] = location.longitude

    with open('../processed/bars_nb_latlong.json', 'w') as outfile:
        json.dump(bar_dict, outfile, indent=2)


if __name__ == "__main__":
    main()
