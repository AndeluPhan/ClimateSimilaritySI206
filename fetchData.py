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

def getClimateData(conn, cur):
    # get climate normals (30 years of data per city)
    
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
    conn.commit()
    # main attributes: 
        # month -> "(min apparent temp, max app temp, monthly precip_sum, monthly shortwave_radiation_sum, monthly max wind speed)"

    # 1 table, city -> 12 cols, one col represents 1 month, 1 cell rep ***store as a string. ***

    cur.execute("""SELECT * FROM population""")
    rows = cur.fetchall()
    for row in rows: # 1 row = 1 city. 
        lat = row[-2]
        lon = row[-1]
        url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date=2003-03-27&end_date=2023-04-10&daily=apparent_temperature_max,apparent_temperature_min,precipitation_sum,windspeed_10m_max,shortwave_radiation_sum&timezone=America/New_York&temperature_unit=fahrenheit"
        res = requests.get(url).json()

        timeStamps = res["daily"]["time"]
        tempMaxs = res["daily"]["apparent_temperature_max"]
        tempMins = res["daily"]["apparent_temperature_min"]
        precipSums = res["daily"]["precipitation_sum"]
        windSpeeds = res["daily"]["windspeed_10m_max"]
        solarRadSums = res["daily"]["shortwave_radiation_sum"]

        # sum everything to be averaged monthly later. 
        monthStatSums = {}
        monthStatCounts = {}
        for i in range(len(timeStamps)):
            month = timeStamps[i].split("-")[1]
            if month not in monthStatSums:
                monthStatSums[month] = {}
                monthStatCounts[month] = {}
            if tempMaxs[i] != None:
                monthStatSums[month]["t_max"] = monthStatSums[month].get("t_max", 0) + tempMaxs[i]
                monthStatCounts[month]["t_max"] = monthStatCounts[month].get("t_max", 0) + 1
            if tempMins[i] != None:
                monthStatSums[month]["t_min"] = monthStatSums[month].get("t_min", 0) + tempMins[i]
                monthStatCounts[month]["t_min"] = monthStatCounts[month].get("t_min", 0) + 1
            if precipSums[i] != None:
                monthStatSums[month]["pcip_sum"] = monthStatSums[month].get("pcip_sum", 0) + precipSums[i]
                monthStatCounts[month]["pcip_sum"] = monthStatCounts[month].get("pcip_sum", 0) + 1
            if windSpeeds[i] != None:    
                monthStatSums[month]["wind_spd"] = monthStatSums[month].get("wind_spd", 0) + windSpeeds[i]
                monthStatCounts[month]["wind_spd"] = monthStatCounts[month].get("wind_spd", 0) + 1
            if solarRadSums[i] != None:
                monthStatSums[month]["solar_rad_sum"] = monthStatSums[month].get("solar_rad_sum", 0) + solarRadSums[i]
                monthStatCounts[month]["solar_rad_sum"] = monthStatCounts[month].get("solar_rad_sum", 0) + 1
        monthStatAvg = {}
        for month in monthStatSums:
            monthStatAvg[month] = {}
            for stat in monthStatSums[month]:
                stat_sum = monthStatSums[month][stat]
                stat_count = monthStatCounts[month][stat]
                monthStatAvg[month][stat] = stat_sum / stat_count

        
        # print(monthStatAvg)

        january = f"{monthStatAvg['01']['t_max']},{monthStatAvg['01']['t_min']},{monthStatAvg['01']['pcip_sum']},{monthStatAvg['01']['wind_spd']},{monthStatAvg['01']['solar_rad_sum']}"
        february = f"{monthStatAvg['02']['t_max']},{monthStatAvg['02']['t_min']},{monthStatAvg['02']['pcip_sum']},{monthStatAvg['02']['wind_spd']},{monthStatAvg['02']['solar_rad_sum']}"
        march = f"{monthStatAvg['03']['t_max']},{monthStatAvg['03']['t_min']},{monthStatAvg['03']['pcip_sum']},{monthStatAvg['03']['wind_spd']},{monthStatAvg['03']['solar_rad_sum']}"
        april = f"{monthStatAvg['04']['t_max']},{monthStatAvg['04']['t_min']},{monthStatAvg['04']['pcip_sum']},{monthStatAvg['04']['wind_spd']},{monthStatAvg['04']['solar_rad_sum']}"

        may = f"{monthStatAvg['05']['t_max']},{monthStatAvg['05']['t_min']},{monthStatAvg['05']['pcip_sum']},{monthStatAvg['05']['wind_spd']},{monthStatAvg['05']['solar_rad_sum']}"
        june = f"{monthStatAvg['06']['t_max']},{monthStatAvg['06']['t_min']},{monthStatAvg['06']['pcip_sum']},{monthStatAvg['06']['wind_spd']},{monthStatAvg['06']['solar_rad_sum']}"
        july = f"{monthStatAvg['07']['t_max']},{monthStatAvg['07']['t_min']},{monthStatAvg['07']['pcip_sum']},{monthStatAvg['07']['wind_spd']},{monthStatAvg['07']['solar_rad_sum']}"
        august = f"{monthStatAvg['08']['t_max']},{monthStatAvg['08']['t_min']},{monthStatAvg['08']['pcip_sum']},{monthStatAvg['08']['wind_spd']},{monthStatAvg['08']['solar_rad_sum']}"

        september = f"{monthStatAvg['09']['t_max']},{monthStatAvg['09']['t_min']},{monthStatAvg['09']['pcip_sum']},{monthStatAvg['09']['wind_spd']},{monthStatAvg['09']['solar_rad_sum']}"
        october = f"{monthStatAvg['10']['t_max']},{monthStatAvg['10']['t_min']},{monthStatAvg['10']['pcip_sum']},{monthStatAvg['10']['wind_spd']},{monthStatAvg['10']['solar_rad_sum']}"
        november = f"{monthStatAvg['11']['t_max']},{monthStatAvg['11']['t_min']},{monthStatAvg['11']['pcip_sum']},{monthStatAvg['11']['wind_spd']},{monthStatAvg['11']['solar_rad_sum']}"
        december = f"{monthStatAvg['12']['t_max']},{monthStatAvg['12']['t_min']},{monthStatAvg['12']['pcip_sum']},{monthStatAvg['12']['wind_spd']},{monthStatAvg['12']['solar_rad_sum']}"

        insert_sql = """
            INSERT OR IGNORE INTO climateData 
                (january, february, march, april, may, june, july, august, september, october, november , december)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """
        cur.execute(insert_sql, (january, february, march, april, may, june, july, august, september, october, november, december))

        break # test for one row rn. 
    
    conn.commit()
    # each cell in the database pertains to a string serialized "[0.1, 0.2, 0.4, ...]"" representings t_max, t_min, etc...




def main():
    # 100 cities = run 8 times, 4 for population, 4 for climate_data
    conn = sqlite3.connect("climateProject.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM climateData")
    rows = cur.fetchall()
    for row in rows:
        print(len(row))
        print(row)

    # cur.execute("SELECT * FROM population")
    # if len(cur.fetchall()) == 100:

    # getClimateData(conn, cur)
    # else:
        # getCities(conn, cur)

    

    # cur.execute("DROP TABLE population")
    # cur.execute("DROP TABLE climateData")


    conn.close()

if __name__ == '__main__':
    main()