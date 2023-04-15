# Climate Similarity Project
Given a single city, main goal is to output a rankings of the most similar cities in respect to Climate. 

* main.py

* requirement fulfilment:
  1) Two tables, City Populations and City Climates, join the tables on cityID when creating visuals to display city populations too. 
  2) Two APIs: 
    * Meteostat for ease of use, but not free to a certain point.
    * Alternative https://geocoding-api.open-meteo.com/v1/search?name=Chicago&count=10&language=en&format=json
        From https://open-meteo.com/en/docs/historical-weather-api, also does geocoding and population data. 
    * Need another api to get X US cities with population above 50,000. or just webscrape. 
        https://worldpopulationreview.com/us-cities, API would be easier. 
        https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population
        