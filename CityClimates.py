import sqlite3
import numpy as np
from numpy.linalg import norm

def calculateRankings(chosen_city):
    # 1 cosine similarity represents 1 month. 
    # generate 12 cosine similarities, average and sort. 
    conn = sqlite3.connect("climateProject.db")
    cur = conn.cursor()
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
    print(sorted_similarities)
    f = open("calculated_data.txt", 'w')
    f.write(f"Climate cosine similarities between {chosen_city} and 99 other cities\n")
    for city in sorted_similarities:
        f.write(f"{city[0]}: {city[1]}\n")
    
    f.write(f"\nCity with the most similar climate to {chosen_city}: {sorted_similarities[0][0]}\n")
    f.write(f"City with the least similar climate to {chosen_city}: {sorted_similarities[-1][0]}\n")


def main():
    city = input("Enter a city: ")
    calculateRankings(city)


if __name__ == '__main__':
    main()

