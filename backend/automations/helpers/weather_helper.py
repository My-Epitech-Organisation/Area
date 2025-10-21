##
## EPITECH PROJECT, 2025
## Area
## File description:
## weather_helper
##

"""Weather API helper functions for actions and reactions."""

import logging
import time
from functools import lru_cache
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openweathermap.org/data/2.5"


@lru_cache(maxsize=32)
# The 'key' parameter is intentionally unused in the function body.
# It exists solely to create unique cache entries for lru_cache,
# allowing cache invalidation based on location, units, and time.
def cached_weather(api_key, location, units, key):
    return get_weather_data(api_key, location, units)


def get_weather_data_cached(api_key, location, units="metric"):
    now = int(time.time() // 900)  # Cache for 15 minutes
    key = f"{location}:{units}:{now}"
    return cached_weather(api_key, location, units, key)


def get_weather_data(api_key: str, location: str, units: str = "metric") -> Dict:
    """
    Get current weather data for a location.
    """
    if not api_key or not location:
        raise ValueError("API key and location are required")

    # Validate and default units
    valid_units = ["metric", "imperial", "standard"]
    if units not in valid_units:
        units = "metric"

    try:
        base_url = BASE_URL + "/weather"
        params = {
            "q": location,
            "appid": api_key,
            "units": units,
        }

        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        logger.info(
            f"Retrieved weather for {location}: {data.get('weather', [{}])[0].get('description', 'unknown')}"
        )

        return {
            "location": location,
            "temperature": data.get("main", {}).get("temp"),
            "humidity": data.get("main", {}).get("humidity"),
            "pressure": data.get("main", {}).get("pressure"),
            "description": data.get("weather", [{}])[0].get("description"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "units": units,
        }

    except requests.RequestException as e:
        logger.error(f"Weather API failed for {location}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_weather_data: {e}")
        raise


def check_weather_condition(
    api_key: str, location: str, condition: str, threshold: float = None
) -> bool:
    """
    Check if a specific weather condition is met.
    """
    try:
        weather_data = get_weather_data(api_key, location)
        weather_desc = weather_data.get("description", "").lower()
        weather_temp = weather_data.get("temperature", 0)

        if condition == "rain":
            return "rain" in weather_desc
        elif condition == "snow":
            return "snow" in weather_desc
        elif condition == "extreme heat":
            return weather_temp > (threshold or 35)
        elif condition == "extreme cold":
            return weather_temp < (threshold or -10)
        elif condition == "windy":
            return weather_data.get("wind_speed", 0) > (threshold or 10)

        return False

    except Exception as e:
        logger.error(f"Error checking weather condition {condition}: {e}")
        return False


def get_forecast(
    api_key: str, location: str, days: int = 5, units: str = "metric"
) -> List[Dict]:
    """
    Get weather forecast for multiple days.
    """
    if not api_key or not location:
        raise ValueError("API key and location are required")

    # Validate and default units
    valid_units = ["metric", "imperial", "standard"]
    if units not in valid_units:
        units = "metric"

    try:
        base_url = BASE_URL + "/forecast"
        params = {
            "q": location,
            "appid": api_key,
            "units": units,
            "cnt": days * 8,  # 8 forecasts per day
        }

        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Process forecast data
        forecast = []
        for item in data.get("list", [])[::8]:  # Every 8th item (daily)
            forecast.append(
                {
                    "date": item.get("dt_txt"),
                    "temperature": item.get("main", {}).get("temp"),
                    "description": item.get("weather", [{}])[0].get("description"),
                    "humidity": item.get("main", {}).get("humidity"),
                }
            )

        logger.info(f"Retrieved {days}-day forecast for {location}")
        return forecast

    except requests.RequestException as e:
        logger.error(f"Weather forecast API failed for {location}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_forecast: {e}")
        raise


def format_weather_message(weather_data: Dict) -> str:
    """
    Format weather data into a human-readable message.
    """
    if weather_data.get("status") == "not_implemented":
        return "Weather integration not yet configured"

    location = weather_data.get("location", "Unknown")
    temp = weather_data.get("temperature")
    description = weather_data.get("description") or "Unknown"
    humidity = weather_data.get("humidity")
    units_map = {"metric": "°C", "imperial": "°F", "standard": "K"}
    units = units_map.get(weather_data.get("units"), "")

    # Handle None values
    try:
        temp_str = f"{temp:.1f}" if temp is not None else "N/A"
    except Exception as e:
        logger.error(f"Error formatting temperature: {e}")
        temp_str = "N/A"

    try:
        humidity_str = f"{humidity}" if humidity is not None else "N/A"
    except Exception as e:
        logger.error(f"Error formatting humidity: {e}")
        humidity_str = "N/A"

    return (
        f"Weather in {location}: {temp_str}{units}, {description}. "
        f"Humidity: {humidity_str}%"
    )
