#!/usr/bin/python

import psycopg2 
import geopy
from geopy.geocoders import Nominatim

# If you see an error along the lines of:
#
# psycopg2.ProgrammingError: function st_geogfromtext(text) does not exist
# LINE 1: ...bar_address, bar_rating, local_rating, ST_DWithin(ST_GeogFro...
#                                                             ^
# HINT:  No function matches the given name and argument types. You might need to add explicit type casts.
#
# This means that postgis was not enabled for the particular database.
# Enabling can be done by going into the particular database from psql and typing:
#
#   CREATE EXTENSION postgis;
#
# For more information, see this link:
#   http://postgis.net/install/

def main():
    radius = 250
    address = '478 Green St, San Francisco'
    print address
    
    geolocator = Nominatim()
    timeout = 60
    location = geolocator.geocode(address, timeout = timeout)
    print location.longitude
    print location.latitude

    conn = psycopg2.connect("dbname='bars'")
    cur = conn.cursor()

    q = "SELECT bar_name, bar_category_1, bar_address, bar_rating, local_rating, ST_DWithin(ST_GeogFromText('POINT(' || lon || ' ' || lat || ')'),ST_GeogFromText('POINT(%s %s)'), %s) FROM bars;"
    print q % (location.longitude, location.latitude, radius)
    cur.execute(q, (location.longitude, location.latitude, radius))
    query_results = cur.fetchall()
#    print query_results
    keys = ['bar_name', 'bar_category_1', 'bar_address', 'bar_rating', 'local_rating']
    inside = []
    for bar in query_results:
        if bar[5] == True:
            print bar[0]
            inside.append(dict(zip(keys, bar)))
    print inside
    print len(inside)
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
