from flask import render_template, request
from app import app
import pymysql as mdb
import json
import os

db = mdb.connect(user="root", host="localhost", db="world_innodb", charset='utf8')

@app.route('/')
@app.route('/index')
def index():
   user = { 'nickname': 'Laura' },
   return render_template("index.html",
                          title = 'Home',
                          user = user
                          )

@app.route('/return_page', methods=['GET'])
def return_page():
   name = request.args.get('address', None)
   json_bars = os.path.dirname(os.path.realpath(__file__))+'/bars_nb.json'
   bar_dict = json.loads(open(json_bars).read())
#   return_vals = {'key':'value'} #Need to make this real
   return render_template("return_page.html", data=[bar_dict[name], bar_dict[name]])






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
