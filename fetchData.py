import requests
import json
import sqlite3
from bs4 import BeautifulSoup

'''
Fetch data from apis
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
    for row in rows:
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

def getClimateData():
    pass



def main():
    conn = sqlite3.connect("climateProject.db")
    cur = conn.cursor()
    # getCities(conn, cur)
    cur.execute("""
        SELECT * FROM population
    """)
    rows = cur.fetchall()
    for row in rows:
        print(row)

    conn.close()

if __name__ == '__main__':
    main()