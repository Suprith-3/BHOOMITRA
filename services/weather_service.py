import requests
from flask import current_app

class WeatherService:

    def get_weather(self, city="Bangalore"):

        api_key = current_app.config["WEATHER_API_KEY"]

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

        response = requests.get(url)
        data = response.json()

        weather = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["description"]
        }

        return weather