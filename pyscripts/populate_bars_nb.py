#!/usr/bin/python

import json
import psycopg2 

def main():
    
    json_bars = '../processed/bars_nb_rated_prelim.json'
    bars = json.loads(open(json_bars).read())

    conn = psycopg2.connect("dbname='bars_nb'")
    cur = conn.cursor()

    q = "DROP TABLE IF EXISTS bars_nb;"
    cur.execute(q)

    q = "CREATE TABLE bars_nb (bar_name TEXT, bar_address TEXT, lat DOUBLE PRECISION, long DOUBLE PRECISION, bar_num_reviews SMALLINT, bar_rating REAL, local_rating SMALLINT, bar_category_1 TEXT, bar_category_2 TEXT, bar_category_3 TEXT, bar_neighborhood_1 TEXT,  bar_neighborhood_2 TEXT,  bar_neighborhood_3 TEXT, file_name TEXT);"
    cur.execute(q)

    for bar in bars:
        bar_name = bars[bar]['bar_name']
        bar_address = bars[bar]['bar_address']
        lat = bars[bar]['lat']
        long = bars[bar]['long']
        bar_num_reviews = bars[bar]['bar_num_reviews']
        bar_rating = bars[bar]['bar_rating']
        local_rating = bars[bar]['local_rating']
        bar_category_1 = bars[bar]['bar_category_1']
        bar_category_2 = bars[bar]['bar_category_2']
        bar_category_3 = bars[bar]['bar_category_3']
        bar_neighborhood_1 = bars[bar]['bar_neighborhood_1']
        bar_neighborhood_2 = bars[bar]['bar_neighborhood_2']
        bar_neighborhood_3 = bars[bar]['bar_neighborhood_3']

        q = "INSERT INTO bars_nb VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        cur.execute(q, (
                bar_name,
                bar_address,
                lat,
                long,
                bar_num_reviews,
                bar_rating,
                local_rating,
                bar_category_1,
                bar_category_2,
                bar_category_3,
                bar_neighborhood_1,
                bar_neighborhood_2,
                bar_neighborhood_3))
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
