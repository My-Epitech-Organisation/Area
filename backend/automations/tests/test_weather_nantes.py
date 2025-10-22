#!/usr/bin/env python
"""
Test script to call weather API for Nantes and log the response.
"""

import os
import sys

import django

from automations.helpers.weather_helper import get_weather_data

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "area_project.settings")
django.setup()


def test_weather_nantes():
    """Test weather API for Nantes."""
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        print("❌ OPENWEATHERMAP_API_KEY not found in environment")
        return

    location = "Nantes, Pays de la Loire"
    print(f"🌤️  Fetching weather for {location}...")

    try:
        weather_data = get_weather_data(api_key, location)
        print("✅ Weather data retrieved successfully!")
        print(f"📍 Location: {weather_data['location']}")
        print(f"🌡️  Temperature: {weather_data['temperature']}°C")
        print(f"💧 Humidity: {weather_data['humidity']}%")
        print(f"📝 Description: {weather_data['description']}")
        print(f"💨 Wind Speed: {weather_data['wind_speed']} m/s")

        print("\n📄 Check the logs/weather_api.log file for the full API response!")

    except Exception as e:
        print(f"❌ Error fetching weather: {e}")


if __name__ == "__main__":
    test_weather_nantes()
