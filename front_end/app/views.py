from flask import render_template, request, jsonify
from app import app
import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
import json
import os
import geopy
from geopy.geocoders import Nominatim

db = psycopg2.connect("dbname='bars_nb'")#, user='root', host='localhost'") 
geolocator = Nominatim()


@app.route('/')
@app.route('/index')
def index():
   user = { 'nickname': 'Laura' },
   return render_template("index.html",
                          title = 'Home',
                          user = user
                          )

@app.route('/consult', methods=['GET'])
def consult():
   name = request.args.get('address', None)
   #convert name to longitude and latitude (geocoder???)
   timeout = 60
   location = geolocator.geocode(name, timeout = timeout)
   lon = location.longitude
   lati = location.latitude
   with db:
      radius = 1000.0 # meters
      cur = db.cursor()
      q = "SELECT bar_name, bar_category_1, bar_address, bar_rating, local_rating, ST_DWithin(ST_GeogFromText('POINT\
(' || long || ' ' || lat || ')'),ST_GeogFromText('POINT(%s %s)'), %s) FROM bars_nb;"# LIMIT 5;"
      cur.execute(q, (lon, lati, radius))
      query_results = cur.fetchall()
      keys = ['bar_name', 'bar_category_1', 'bar_address', 'bar_rating', 'local_rating']
      inside = []
      for bar in query_results:
        if bar[5] == True:
            inside.append(dict(zip(keys, bar)))
   # Reason for calling flask.jsonify() as opposed to json.dumps()
   #   http://flask.pocoo.org/docs/0.10/security/#json-security
   return jsonify({'results' : inside})

@app.route('/map')
def map():
   user = { 'nickname': 'Laura' },
   return render_template("map_test.html")

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
