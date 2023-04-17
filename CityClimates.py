import sqlite3
import numpy as np
from numpy.linalg import norm
import matplotlib.pyplot as plt
from math import sin, cos, sqrt, atan2, radians

def calculateRankings(cur, conn, chosen_city):
    # 1 cosine similarity represents 1 month. 
    # generate 12 cosine similarities, average and sort. 
    cur.execute("SELECT city_id FROM population WHERE city == ?", (chosen_city, ))
    chosen_city_id = cur.fetchone()[0]
    cur.execute("SELECT * FROM climateData WHERE city_id == ?", (chosen_city_id, ))
    chosen_climate_data = cur.fetchone()
    cur.execute("SELECT climateData.*, population.city FROM climateData JOIN population ON climateData.city_id = population.city_id WHERE climateData.city_id != ?", (chosen_city_id, ))
    climateData = cur.fetchall()
    cosine_similarities = {} # dictionary holding cosine similarities between other cities and chosen city {city_name: cosine_similarity}
    for city in climateData:
        city_name = city[-1]
        # getting cosine similarity for each month
        monthly_similarities = []
        for month in range(1, 13):
            chosen_climate_info = np.array(chosen_climate_data[month].split(','), dtype=float)
            climate_info = np.array(city[month].split(','), dtype=float)
            cosine = np.dot(chosen_climate_info,climate_info)/(norm(chosen_climate_info)*norm(climate_info))
            monthly_similarities.append(cosine)
        # getting the average cosine similarity
        cosine_similarities[city_name] = sum(monthly_similarities) / 12
    # sorting cosine similarities
    sorted_similarities = sorted(cosine_similarities.items(), key=lambda x:x[1], reverse=True)
    f = open("calculated_data.txt", 'w')
    f.write(f"Climate cosine similarities between {chosen_city} and 99 other cities\n")
    for city in sorted_similarities:
        f.write(f"{city[0]}: {city[1]}\n")
    
    f.write(f"\nCity with the most similar climate to {chosen_city}: {sorted_similarities[0][0]}\n")
    f.write(f"City with the least similar climate to {chosen_city}: {sorted_similarities[-1][0]}\n")
    f.close()

    # plotting the top 10 cities with the most similar climate
    city_name = [i[0] for i in sorted_similarities[:10]]
    city_cosine_similarity = [i[1] for i in sorted_similarities[:10]]
    plt.barh(city_name, city_cosine_similarity, color="darkorange")
    plt.xlabel(f"Climate Cosine Similarity to {chosen_city}")
    plt.ylabel("Cities")
    plt.xlim(sorted_similarities[10][1], 1.0000)
    plt.title(f"Top 10 Cities With Similar Climate To {chosen_city}")
    plt.gcf().subplots_adjust(left=0.25)
    plt.savefig("topTenSimilarClimates.png")

    return cosine_similarities

def calculateSimilaritiesByLatLon(cur, conn, city, cosine_similarities):
    cur.execute("SELECT city, lat, lon FROM population WHERE city == ?", (city, ))
    chosen_city_lat_lon = cur.fetchone()
    cur.execute("SELECT city, lat, lon FROM population WHERE city != ?", (city, ))
    city_lat_lon = cur.fetchall()
    latitude_diff = {}
    longitude_diff = {}
    lat1 = chosen_city_lat_lon[1]
    lon1 = chosen_city_lat_lon[2]
    for cities in city_lat_lon:
        lat2 = cities[1]
        lon2 = cities[2]
        lat_diff = abs(lat1 - lat2)
        lon_diff = abs(lon1 - lon2)
        latitude_diff[cities[0]] = lat_diff
        longitude_diff[cities[0]] = lon_diff
    sorted_lat_diff = sorted(latitude_diff.items(), key=lambda x:x[1])
    sorted_lon_diff = sorted(longitude_diff.items(), key=lambda x:x[1])

    f = open("calculated_data.txt", 'a')
    f.write(f"\nCities with the closest latitude to {city}:\n")
    for cities in sorted_lat_diff:
        f.write(f"{cities[0]}, ")
    
    f.write(f"\n\nCities with the closest longitude to {city}:\n")
    for cities in sorted_lon_diff:
        f.write(f"{cities[0]}, ")
    f.close()

    # plotting the lat and lon vs climate similarity
    x_axis1 = []
    y_axis1 = []
    for dist in sorted_lat_diff:
        x_axis1.append(dist[1])
        y_axis1.append(cosine_similarities[dist[0]])
    x_axis2 = []
    y_axis2 = []
    for dist in sorted_lon_diff:
        x_axis2.append(dist[1])
        y_axis2.append(cosine_similarities[dist[0]])
    fig, (ax1, ax2) = plt.subplots(2)
    xlim = max(x_axis1[-1], x_axis2[-1])
    # plotting lat
    ax1.plot(x_axis1, y_axis1, 'hotpink', label="Latitude")
    ax1.set(xlabel="Latitude Difference", ylabel="Climate Cosine Similarity", title=f"Latitude Difference VS Climate Cosine Similarity ({city})")
    ax1.set_xlim(0, xlim)
    ax1.grid()
    # plotting lon
    ax2.plot(x_axis2, y_axis2, 'lightsteelblue', label="Longitude")
    ax2.set(xlabel="Longitude Difference", ylabel="Climate Cosine Similarity", title=f"Longitude Difference VS Climate Cosine Similarity ({city})")
    ax2.set_xlim(0, xlim)
    ax2.grid()
    fig.tight_layout()
    fig.savefig("similarityLatLonPlot.png")
        


def main():
    conn = sqlite3.connect("climateProject.db")
    cur = conn.cursor()
    city = input("Enter a city: ")
    cosine_similarities = calculateRankings(cur, conn, city)
    calculateSimilaritiesByLatLon(cur, conn, city, cosine_similarities)


if __name__ == '__main__':
    main()

