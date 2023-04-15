import requests
import json
import sqlite3
from bs4 import BeautifulSoup

'''
Webscrape from wikipedia U.S Cities (population, lat, lon)
'''
def getCities(conn, cur):
    '''
    Get cities from wikipedia, gets (city, state, population, lat, lon)
    '''
    resp = requests.get("https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population")
    soup = BeautifulSoup(resp.text, 'html.parser');

    sql = """
        CREATE TABLE IF NOT EXISTS population (
            city_id INTEGER PRIMARY KEY, 
            city TEXT,
            state TEXT,
            population INTEGER,
            lat REAL, 
            lon REAL
        )
    """
    cur.execute(sql)

    city_table = soup.find_all("table", class_="wikitable")[1]
    table_body = city_table.find("tbody")
    rows = table_body.find_all("tr")[1:]

    cur.execute("SELECT * FROM population")
    start = len(cur.fetchall())
    end = len(rows) if len(rows) < start + 25 else start + 25
    for row in rows[start:end]:
        data_elems = row.find_all("td")
        city = data_elems[0].get_text()

        if "[" in city:
            end = city.index("[")
            city = city[:end]
        city = city.rstrip()
        state = data_elems[1].get_text().rstrip()
        population = int(data_elems[2].get_text().rstrip().replace(',', ''))
        location = data_elems[-1].get_text()
        coords = location.split("/")[-1].replace(';', '')
        coords = coords.split(" ")
        lat = float(coords[1])
        lon = float(coords[2].replace("\ufeff", ""))

        insert_sql = """
            INSERT OR IGNORE INTO population 
            (city, state, population, lat, lon)
            VALUES (?,?,?,?,?)
        """
        cur.execute(insert_sql, (city, state, population, lat, lon))

    conn.commit()

def getClimateData(cur):
    # get climate normals (30 years of data per city)
    
    # https://archive-api.open-meteo.com/v1/archive?latitude=52.52&longitude=13.41&start_date=2003-03-27&end_date=2023-04-10&daily=apparent_temperature_max,apparent_temperature_min,precipitation_sum,windspeed_10m_max,shortwave_radiation_sum&timezone=America/New_York

    # main attributes: 
        # month -> "(min apparent temp, max app temp, monthly precip_sum, monthly shortwave_radiation_sum, monthly max wind speed)"

    # 1 table, city -> 12 cols, one col represents 1 month, 1 cell rep
    # store as a string. 

    cur.execute("""SELECT * FROM population""")
    rows = cur.fetchall()
    for row in rows:
        print(row)

    # each cell in the database pertains to a string serialized "[0.1, 0.2, 0.4, ...]"" representings t_max, t_min, etc...
    sql = """
        CREATE TABLE IF NOT EXISTS climateData (
            city_id INTEGER PRIMARY KEY, 
            january TEXT,
            february TEXT,
            march TEXT,
            april TEXT,
            may TEXT,
            june TEXT,
            july TEXT,
            august TEXT,
            september TEXT,
            october TEXT,
            november TEXT,
            december TEXT
        )
    """
    cur.execute(sql)



def main():
    # 100 cities = run 8 times, 4 for population, 4 for climate_data
    conn = sqlite3.connect("climateProject.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM population")
    if len(cur.fetchall()) == 100:
        getClimateData(cur)
    else:
        getCities(conn, cur)

    

    # cur.execute("DROP TABLE population")
    # cur.execute("DROP TABLE climateData")


    conn.close()

if __name__ == '__main__':
    main()