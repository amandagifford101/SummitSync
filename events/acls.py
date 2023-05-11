from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY

import json

import requests


# function to request photo from Pexels API
def get_photo(city, state):
    # Create a dictionary for the headers to use in the request
    # Create the URL for the request with the city and state

    params = {"query": f"{city}, {state}", "per_page": 1}
    url = "https://api.pexels.com/v1/search"

    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers, params=params)
    # Make the request
    # Parse the JSON response
    photo_dict = json.loads(response.content)
    # Return a dictionary that contains a `picture_url` key and
    #   one of the URLs for one of the pictures in the response
    try:
        return {"picture_url": photo_dict["photos"][0]["src"]["original"]}
    except (KeyError, IndexError):
        return {"picture_url": None}


# function to request weather data from Open Weather API
def get_weather_data(city, state):
    # Create the URL for the geocoding API with the city and state
    # Make the request
    # Parse the JSON response
    # Get the latitude and longitude from the response

    # Create the URL for the current weather API with the latitude
    #   and longitude
    # Make the request
    # Parse the JSON response
    # Get the main temperature and the weather's description and put
    #   them in a dictionary
    # Return the dictionary
    response = requests.get(
        f"https://api.openweathermap.org/geo/1.0/direct?q={city},{state},USA&limit=5&appid={OPEN_WEATHER_API_KEY}"
    )
    geo_data = json.loads(response.content)
    latitude = geo_data[0].get("lat")
    longitude = geo_data[0].get("lon")

    weather_response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={OPEN_WEATHER_API_KEY}"
    )
    weather_data = json.loads(weather_response.content)
    weather = {
        "temperature": weather_data["main"]["temp"],
        "description": weather_data["weather"][0]["description"],
    }
    return weather
