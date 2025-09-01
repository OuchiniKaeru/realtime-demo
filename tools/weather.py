import httpx
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class WeatherResponse(BaseModel):
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    unit_temperature: str = "celsius"
    unit_precipitation: str = "mm"
    unit_wind: str = "km/h"
    forecast_daily: list
    current_time: str
    latitude: float
    longitude: float
    location_name: str
    weather_code: int

async def get_weather(location: str):
    try:
        async with httpx.AsyncClient() as client:
            # Get coordinates for location
            geocoding_response = await client.get(
                f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
            )
            geocoding_data = geocoding_response.json()
            
            if not geocoding_data.get("results"):
                return {"error": f"Could not find coordinates for {location}"}
                
            lat = geocoding_data["results"][0]["latitude"]
            lon = geocoding_data["results"][0]["longitude"]
            location_name = geocoding_data["results"][0]["name"]
            
            # Get weather data with more parameters
            weather_response = await client.get(
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code"
                f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
                f"&timezone=auto"
                f"&forecast_days=7"
            )
            weather_data = weather_response.json()
            
            # Extract current weather
            current = weather_data["current"]
            daily = weather_data["daily"]
            
            # Create daily forecast array
            forecast = []
            for i in range(len(daily["time"])):
                forecast.append({
                    "date": daily["time"][i],
                    "max_temp": daily["temperature_2m_max"][i],
                    "min_temp": daily["temperature_2m_min"][i],
                    "precipitation": daily["precipitation_sum"][i],
                    "weather_code": daily["weather_code"][i]
                })
            
            return WeatherResponse(
                temperature=current["temperature_2m"],
                humidity=current["relative_humidity_2m"],
                precipitation=current["precipitation"],
                wind_speed=current["wind_speed_10m"],
                forecast_daily=forecast,
                current_time=current["time"],
                latitude=lat,
                longitude=lon,
                location_name=location_name,
                weather_code=current["weather_code"]
            )
            
    except Exception as e:
        logger.error(f"Error getting weather data: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Could not get weather data: {str(e)}"})
