#!/usr/bin/python

import json
import sys
import geopy
from geopy.geocoders import Nominatim
import re

def main():

    geolocator = Nominatim()

    json_bars = '../processed/bars.json'
    bar_dict = json.loads(open(json_bars).read())

    bar_reviews = {}
    search = "San Francisco, CA"
    timeout = 60
    bad_key = []

    total = len(bar_dict)
    if True:
        for (cnt, key) in enumerate(bar_dict):
            print "Processing (%d/%d)" % (cnt+1, total)
            s = re.search("(.*)" + search, bar_dict[key]['bar_address'])
            if not s:
              # If there is not result for the search, its beacuse the bar is likely not in San Francisco
              # For example: 22 Hillcrest Dr, Daly City, CA 94014
              bad_key.append(key)
              continue
            address = s.group(1) + search
            try:
                location = geolocator.geocode(address, timeout = timeout)
                print address
                print (location.latitude, location.longitude),
                if location.latitude > 37.83 or location.latitude < 37.7 or location.longitude > -122.35 or location.longitude < -122.55:
                  print "(skipping)"
                  bad_key.append(key)
                  continue
                else:
                  print
                bar_dict[key]['lat'] = location.latitude
                bar_dict[key]['lon'] = location.longitude
            except AttributeError:
                sys.stdout.write('Address not valid.  Removing %s\n' % bar_dict[key]['bar_name'])
                bad_key.append(key)
            except geopy.exc.GeocoderTimedOut:
                sys.stdout.write('Geocoder timed out.  Removing %s\n' % bar_dict[key]['bar_name'])
                bad_key.append(key)
                continue

        for key in bad_key:
            del bar_dict[key]


    with open('../processed/bars_latlon.json', 'w') as outfile:
        json.dump(bar_dict, outfile, indent=2)


if __name__ == "__main__":
    main()
