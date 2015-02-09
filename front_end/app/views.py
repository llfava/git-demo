from flask import render_template, request, jsonify, send_file
from app import app
import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
import json
import os
import geopy
from geopy.geocoders import Nominatim

db = psycopg2.connect("dbname='bars'")#, user='root', host='localhost'") 
geolocator = Nominatim()


@app.route('/')
@app.route('/index')
def index():
   user = { 'nickname': 'Laura' },
   return render_template("index.html",
                          title = 'Home',
                          user = user
                          )

@app.route('/about', methods=['GET'])
def about():
    return send_file("./static/slides/demo.pdf")

# TODO:
# Figure out why these addresses can't be processed by geolocator:
#  2200 Mason St San Francisco, CA 94133
#
@app.route('/consult', methods=['GET'])
def consult():
   name = request.args.get('address', None)
   # Convert name to longitude and latitude (geocoder)
   location = geolocator.geocode(name, timeout=60)
   if location == None:
     # If location==None, then the geolocator failed to parse the address
     # For example, geolocator can't parse the address "2200 Mason St San Francisco, CA 94133"
     return jsonify({'error' : 'Address error'})
   with db:
      radius = 1000.0 # meters
      cur = db.cursor()
      q = "SELECT bar_name, bar_category_1, bar_address, bar_rating, local_rating, lat, lon, file_name, ST_DWithin(ST_GeogFromText('POINT(' || lon || ' ' || lat || ')'),ST_GeogFromText('POINT(%s %s)'), %s) FROM bars ORDER by bar_rating DESC, local_rating;"# LIMIT 5;"
      cur.execute(q, (location.longitude, location.latitude, radius))
      query_results = cur.fetchall()
      keys = ['bar_name', 'bar_category_1', 'bar_address', 'bar_rating', 'local_rating', 'lat', 'lon', 'file_name']
      inside = []
      for bar in query_results:
        if bar[-1] == True:
            inside.append(dict(zip(keys, bar)))
   # Reason for calling flask.jsonify() as opposed to json.dumps()
   #   http://flask.pocoo.org/docs/0.10/security/#json-security
   return jsonify({'results' : inside, 'location' : (location.latitude,location.longitude)})

@app.route('/map')
def map():
   user = { 'nickname': 'Laura' },
   return render_template("map_test.html")

@app.route('/osm')
def osm():
   user = { 'nickname': 'Laura' },
   return render_template("osm.html")

@app.route('/db')
def cities_page():
   with db:
      cur = db.cursor()
      cur.execute("SELECT Name FROM City LIMIT 15;")
      query_results = cur.fetchall()
   cities = ""
   for result in query_results:
      cities += result[0]
      cities += "<br>"
   return cities

@app.route("/db_fancy")
def cities_page_fancy():
    with db:
        cur = db.cursor()
        cur.execute("SELECT Name, CountryCode, Population FROM City ORDER BY Population LIMIT 15;")

        query_results = cur.fetchall()
    cities = []
    for result in query_results:
        cities.append(dict(name=result[0], country=result[1], population=result[2]))
    return render_template('cities.html', cities=cities)
