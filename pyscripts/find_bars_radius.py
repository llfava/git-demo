#!/usr/bin/python

import psycopg2 
import geopy
from geopy.geocoders import Nominatim


def main():
    radius = 250
    address = '478 Green St, San Francisco'
    print address
    
    geolocator = Nominatim()
    timeout = 60
    location = geolocator.geocode(address, timeout = timeout)
    lon = location.longitude 
    lati = location.latitude


    conn = psycopg2.connect("dbname='bars_nb'")
    cur = conn.cursor()

    q = "SELECT bar_name, bar_category_1, bar_address, bar_rating, local_rating, ST_DWithin(ST_GeogFromText('POINT(' || long || ' ' || lat || ')'),ST_GeogFromText('POINT(%s %s)'), %s) FROM bars_nb;"
    cur.execute(q, (lon, lati, radius))
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
