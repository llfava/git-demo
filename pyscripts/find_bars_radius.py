#!/usr/bin/python

import psycopg2 

def main():
    

    conn = psycopg2.connect("dbname='bars_nb'")
    cur = conn.cursor()

#    q = "CREATE EXTENSION postgis;"
#    cur.execute(q)
#    q = "SELECT postgis_full_version();"
#    cur.execute(q)

    q = "SELECT ST_DWithin(ST_GeogFromText('POINT(' || long || ' ' || lat || ')'),ST_GeogFromText('POINT(-122.4015726 37.8006544)'), 500.0) FROM bars_nb;"
    cur.execute(q)
    rows = cur.fetchall()
    
    for row in rows:
        print row

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
