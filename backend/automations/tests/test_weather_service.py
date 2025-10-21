"""
Unit tests for weather service functions.

Tests cover:
- Weather data retrieval from OpenWeatherMap API
- Weather condition checking logic
- Forecast data retrieval
- Message formatting
- Error handling and validation
- Caching functionality
"""

import json
from unittest.mock import MagicMock, patch

from django.test import TestCase

from automations.helpers.weather_helper import (
    check_weather_condition,
    format_weather_message,
    get_forecast,
    get_weather_data,
    get_weather_data_cached,
)


class WeatherServiceTest(TestCase):
    """Test weather service helper functions."""

    def setUp(self):
        """Set up test data and mock API responses."""
        self.valid_api_key = "test_api_key_123"
        self.invalid_api_key = ""
        self.location = "Paris,FR"
        self.invalid_location = ""

        # Mock OpenWeatherMap API responses
        self.weather_api_response = {
            "coord": {"lon": 2.3488, "lat": 48.8534},
            "weather": [
                {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
            ],
            "base": "stations",
            "main": {
                "temp": 20.5,
                "feels_like": 19.8,
                "temp_min": 18.2,
                "temp_max": 22.1,
                "pressure": 1013,
                "humidity": 65,
                "sea_level": 1013,
                "grnd_level": 1009,
            },
            "visibility": 10000,
            "wind": {"speed": 3.5, "deg": 240, "gust": 5.2},
            "clouds": {"all": 20},
            "dt": 1640995200,
            "sys": {
                "type": 2,
                "id": 2011048,
                "country": "FR",
                "sunrise": 1640968934,
                "sunset": 1640998374,
            },
            "timezone": 3600,
            "id": 2988507,
            "name": "Paris",
            "cod": 200,
        }

        self.forecast_api_response = {
            "cod": "200",
            "message": 0,
            "cnt": 16,  # 2 days * 8 forecasts per day
            "list": [
                # Day 1 forecasts (8 entries, 3-hour intervals)
                {
                    "dt": 1640995200,
                    "main": {
                        "temp": 20.5,
                        "feels_like": 19.8,
                        "temp_min": 18.2,
                        "temp_max": 22.1,
                        "pressure": 1013,
                        "sea_level": 1013,
                        "grnd_level": 1009,
                        "humidity": 65,
                        "temp_kf": 0,
                    },
                    "weather": [
                        {
                            "id": 800,
                            "main": "Clear",
                            "description": "clear sky",
                            "icon": "01d",
                        }
                    ],
                    "clouds": {"all": 20},
                    "wind": {"speed": 3.5, "deg": 240, "gust": 5.2},
                    "visibility": 10000,
                    "pop": 0,
                    "sys": {"pod": "d"},
                    "dt_txt": "2022-01-01 12:00:00",
                },
                {
                    "dt": 1641006000,
                    "main": {"temp": 18.3, "humidity": 72},
                    "weather": [{"description": "light rain"}],
                    "dt_txt": "2022-01-01 15:00:00",
                },
                {
                    "dt": 1641016800,
                    "main": {"temp": 16.8, "humidity": 78},
                    "weather": [{"description": "moderate rain"}],
                    "dt_txt": "2022-01-01 18:00:00",
                },
                {
                    "dt": 1641027600,
                    "main": {"temp": 15.2, "humidity": 82},
                    "weather": [{"description": "heavy rain"}],
                    "dt_txt": "2022-01-01 21:00:00",
                },
                {
                    "dt": 1641038400,
                    "main": {"temp": 14.1, "humidity": 85},
                    "weather": [{"description": "overcast clouds"}],
                    "dt_txt": "2022-01-02 00:00:00",
                },
                {
                    "dt": 1641049200,
                    "main": {"temp": 13.8, "humidity": 87},
                    "weather": [{"description": "scattered clouds"}],
                    "dt_txt": "2022-01-02 03:00:00",
                },
                {
                    "dt": 1641052800,
                    "main": {"temp": 15.6, "humidity": 79},
                    "weather": [{"description": "few clouds"}],
                    "dt_txt": "2022-01-02 06:00:00",
                },
                {
                    "dt": 1641063600,
                    "main": {"temp": 18.9, "humidity": 68},
                    "weather": [{"description": "clear sky"}],
                    "dt_txt": "2022-01-02 09:00:00",
                },
                # Day 2 forecasts (8 more entries)
                {
                    "dt": 1641074400,
                    "main": {"temp": 22.1, "humidity": 60},
                    "weather": [{"description": "clear sky"}],
                    "dt_txt": "2022-01-02 12:00:00",
                },
                {
                    "dt": 1641085200,
                    "main": {"temp": 19.8, "humidity": 65},
                    "weather": [{"description": "few clouds"}],
                    "dt_txt": "2022-01-02 15:00:00",
                },
                {
                    "dt": 1641096000,
                    "main": {"temp": 17.2, "humidity": 72},
                    "weather": [{"description": "scattered clouds"}],
                    "dt_txt": "2022-01-02 18:00:00",
                },
                {
                    "dt": 1641106800,
                    "main": {"temp": 15.5, "humidity": 78},
                    "weather": [{"description": "broken clouds"}],
                    "dt_txt": "2022-01-02 21:00:00",
                },
                {
                    "dt": 1641117600,
                    "main": {"temp": 14.2, "humidity": 82},
                    "weather": [{"description": "overcast clouds"}],
                    "dt_txt": "2022-01-03 00:00:00",
                },
                {
                    "dt": 1641128400,
                    "main": {"temp": 13.9, "humidity": 85},
                    "weather": [{"description": "light rain"}],
                    "dt_txt": "2022-01-03 03:00:00",
                },
                {
                    "dt": 1641132000,
                    "main": {"temp": 15.8, "humidity": 75},
                    "weather": [{"description": "moderate rain"}],
                    "dt_txt": "2022-01-03 06:00:00",
                },
                {
                    "dt": 1641142800,
                    "main": {"temp": 18.5, "humidity": 68},
                    "weather": [{"description": "clear sky"}],
                    "dt_txt": "2022-01-03 09:00:00",
                },
            ],
            "city": {
                "id": 2988507,
                "name": "Paris",
                "coord": {"lat": 48.8534, "lon": 2.3488},
                "country": "FR",
                "population": 2138551,
                "timezone": 3600,
                "sunrise": 1640968934,
                "sunset": 1640998374,
            },
        }

    @patch("automations.helpers.weather_helper.requests.get")
    def test_get_weather_data_success(self, mock_get):
        """Test successful weather data retrieval."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.weather_api_response
        mock_get.return_value = mock_response

        result = get_weather_data(self.valid_api_key, self.location)

        # Verify API call was made correctly
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": self.location,
                "appid": self.valid_api_key,
                "units": "metric",
            },
            timeout=10,
        )

        # Verify returned data structure
        self.assertEqual(result["location"], self.location)
        self.assertEqual(result["temperature"], 20.5)
        self.assertEqual(result["humidity"], 65)
        self.assertEqual(result["pressure"], 1013)
        self.assertEqual(result["description"], "clear sky")
        self.assertEqual(result["wind_speed"], 3.5)
        self.assertEqual(result["units"], "metric")

    @patch("automations.helpers.weather_helper.requests.get")
    def test_get_weather_data_imperial_units(self, mock_get):
        """Test weather data retrieval with imperial units."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.weather_api_response
        mock_get.return_value = mock_response

        result = get_weather_data(self.valid_api_key, self.location, units="imperial")

        self.assertEqual(result["units"], "imperial")
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": self.location,
                "appid": self.valid_api_key,
                "units": "imperial",
            },
            timeout=10,
        )

    def test_get_weather_data_missing_api_key(self):
        """Test weather data retrieval with missing API key."""
        with self.assertRaises(ValueError) as context:
            get_weather_data(self.invalid_api_key, self.location)

        self.assertIn("API key and location are required", str(context.exception))

    def test_get_weather_data_missing_location(self):
        """Test weather data retrieval with missing location."""
        with self.assertRaises(ValueError) as context:
            get_weather_data(self.valid_api_key, self.invalid_location)

        self.assertIn("API key and location are required", str(context.exception))

    @patch("automations.helpers.weather_helper.requests.get")
    def test_get_weather_data_api_error(self, mock_get):
        """Test weather data retrieval with API error."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response

        with self.assertRaises(Exception) as context:
            get_weather_data(self.valid_api_key, self.location)

        self.assertIn("API Error", str(context.exception))

    @patch("automations.helpers.weather_helper.requests.get")
    def test_get_weather_data_request_exception(self, mock_get):
        """Test weather data retrieval with request exception."""
        from requests.exceptions import RequestException

        mock_get.side_effect = RequestException("Network error")

        with self.assertRaises(RequestException) as context:
            get_weather_data(self.valid_api_key, self.location)

        self.assertIn("Network error", str(context.exception))

    @patch("automations.helpers.weather_helper.requests.get")
    def test_get_forecast_success(self, mock_get):
        """Test successful forecast data retrieval."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.forecast_api_response
        mock_get.return_value = mock_response

        result = get_forecast(self.valid_api_key, self.location, days=2)

        # Verify API call
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "q": self.location,
                "appid": self.valid_api_key,
                "units": "metric",
                "cnt": 16,  # 2 days * 8 forecasts per day
            },
            timeout=10,
        )

        # Verify forecast data (should return 2 entries for 2 days)
        self.assertEqual(len(result), 2)
        self.assertIn("date", result[0])
        self.assertIn("temperature", result[0])
        self.assertIn("description", result[0])
        self.assertIn("humidity", result[0])

    @patch("automations.helpers.weather_helper.requests.get")
    def test_get_forecast_with_imperial_units(self, mock_get):
        """Test forecast retrieval with imperial units."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.forecast_api_response
        mock_get.return_value = mock_response

        result = get_forecast(
            self.valid_api_key, self.location, days=1, units="imperial"
        )

        self.assertEqual(len(result), 2)  # Mock has 16 items, every 8th gives 2 results
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "q": self.location,
                "appid": self.valid_api_key,
                "units": "imperial",
                "cnt": 8,  # 1 day * 8 forecasts per day
            },
            timeout=10,
        )

    @patch("automations.helpers.weather_helper.requests.get")
    def test_get_forecast_api_error(self, mock_get):
        """Test forecast retrieval with API error."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Forecast API Error")
        mock_get.return_value = mock_response

        with self.assertRaises(Exception) as context:
            get_forecast(self.valid_api_key, self.location)

        self.assertIn("Forecast API Error", str(context.exception))

    @patch("automations.helpers.weather_helper.requests.get")
    def test_check_weather_condition_storm(self, mock_get):
        """Test storm condition checking."""
        stormy_response = self.weather_api_response.copy()
        stormy_response["weather"][0]["description"] = "thunderstorm with heavy rain"

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = stormy_response
        mock_get.return_value = mock_response

        result = check_weather_condition(self.valid_api_key, self.location, "storm")
        self.assertFalse(result)  # storm condition not implemented yet

    @patch("automations.helpers.weather_helper.requests.get")
    def test_check_weather_condition_with_custom_thresholds(self, mock_get):
        """Test condition checking with various custom thresholds."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.weather_api_response
        mock_get.return_value = mock_response

        # Test windy with custom threshold
        windy_response = self.weather_api_response.copy()
        windy_response["wind"]["speed"] = 8.0  # Below default threshold of 10

        mock_response.json.return_value = windy_response
        result = check_weather_condition(
            self.valid_api_key, self.location, "windy", threshold=5
        )
        self.assertTrue(result)  # Should be true with lower threshold

    def test_format_weather_message_edge_cases(self):
        """Test weather message formatting with various edge cases."""
        # Test with minimal data
        minimal_data = {
            "location": "Test City",
            "temperature": 25.0,
            "description": "sunny",
            "units": "metric",  # Specify metric units explicitly
        }

        result = format_weather_message(minimal_data)
        expected = "Weather in Test City: 25.0°C, sunny. Humidity: N/A%"
        self.assertEqual(result, expected)

        # Test with all None values
        none_data = {
            "location": None,
            "temperature": None,
            "description": None,
            "humidity": None,
            "units": "metric",
        }

        result = format_weather_message(none_data)
        expected = "Weather in None: N/A°C, Unknown. Humidity: N/A%"
        self.assertEqual(result, expected)

    @patch("automations.helpers.weather_helper.requests.get")
    def test_get_weather_data_with_different_units(self, mock_get):
        """Test weather data retrieval with different unit systems."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.weather_api_response
        mock_get.return_value = mock_response

        # Test standard metric
        result_metric = get_weather_data(
            self.valid_api_key, self.location, units="metric"
        )
        self.assertEqual(result_metric["units"], "metric")

        # Test imperial
        result_imperial = get_weather_data(
            self.valid_api_key, self.location, units="imperial"
        )
        self.assertEqual(result_imperial["units"], "imperial")

        # Test invalid units (should default to metric)
        result_default = get_weather_data(
            self.valid_api_key, self.location, units="invalid"
        )
        self.assertEqual(result_default["units"], "metric")

    @patch("automations.helpers.weather_helper.logger")
    @patch("automations.helpers.weather_helper.requests.get")
    def test_forecast_logging_on_success(self, mock_get, mock_logger):
        """Test that successful forecast calls are logged."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.forecast_api_response
        mock_get.return_value = mock_response

        get_forecast(self.valid_api_key, self.location, days=2)

        # Verify info logging was called
        mock_logger.info.assert_called_once()
        log_call = mock_logger.info.call_args[0][0]
        self.assertIn("Retrieved 2-day forecast for", log_call)
        self.assertIn(self.location, log_call)

    @patch("automations.helpers.weather_helper.logger")
    @patch("automations.helpers.weather_helper.requests.get")
    def test_forecast_logging_on_error(self, mock_get, mock_logger):
        """Test that forecast API errors are logged."""
        from requests.exceptions import RequestException

        mock_get.side_effect = RequestException("Forecast API Error")

        with self.assertRaises(RequestException):
            get_forecast(self.valid_api_key, self.location)

        # Verify error logging was called
        mock_logger.error.assert_called_once()
        log_call = mock_logger.error.call_args[0][0]
        self.assertIn("Weather forecast API failed for", log_call)
        self.assertIn(self.location, log_call)
        self.assertIn("Forecast API Error", log_call)

    def test_get_weather_alerts_returns_empty_list(self):
        """Test that weather alerts returns empty list (not implemented)."""
        result = (
            get_weather_data.__wrapped__.__defaults__[0]
            if hasattr(get_weather_data, "__wrapped__")
            else []
        )
        # Actually call the function
        from automations.helpers.weather_helper import get_weather_alerts

        result = get_weather_alerts(self.valid_api_key, self.location)
        self.assertEqual(result, [])

    @patch("automations.helpers.weather_helper.requests.get")
    def test_condition_check_with_malformed_api_response(self, mock_get):
        """Test condition checking with malformed API response."""
        malformed_response = {"invalid": "data"}

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = malformed_response
        mock_get.return_value = mock_response

        # Should return False for any condition when data is malformed
        result = check_weather_condition(self.valid_api_key, self.location, "rain")
        self.assertFalse(result)

    def test_get_forecast_missing_parameters(self):
        """Test forecast retrieval with missing parameters."""
        with self.assertRaises(ValueError):
            get_forecast("", self.location)

        with self.assertRaises(ValueError):
            get_forecast(self.valid_api_key, "")

    @patch("automations.helpers.weather_helper.requests.get")
    def test_check_weather_condition_rain(self, mock_get):
        """Test rain condition checking."""
        # Mock rainy weather
        rainy_response = self.weather_api_response.copy()
        rainy_response["weather"][0]["description"] = "moderate rain"
        rainy_response["main"]["temp"] = 15.0

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = rainy_response
        mock_get.return_value = mock_response

        result = check_weather_condition(self.valid_api_key, self.location, "rain")
        self.assertTrue(result)

    @patch("automations.helpers.weather_helper.requests.get")
    def test_check_weather_condition_snow(self, mock_get):
        """Test snow condition checking."""
        snowy_response = self.weather_api_response.copy()
        snowy_response["weather"][0]["description"] = "light snow"

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = snowy_response
        mock_get.return_value = mock_response

        result = check_weather_condition(self.valid_api_key, self.location, "snow")
        self.assertTrue(result)

    @patch("automations.helpers.weather_helper.requests.get")
    def test_check_weather_condition_extreme_heat(self, mock_get):
        """Test extreme heat condition checking."""
        hot_response = self.weather_api_response.copy()
        hot_response["main"]["temp"] = 40.0  # Very hot

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = hot_response
        mock_get.return_value = mock_response

        result = check_weather_condition(
            self.valid_api_key, self.location, "extreme heat"
        )
        self.assertTrue(result)

    @patch("automations.helpers.weather_helper.requests.get")
    def test_check_weather_condition_extreme_heat_with_threshold(self, mock_get):
        """Test extreme heat condition with custom threshold."""
        hot_response = self.weather_api_response.copy()
        hot_response["main"]["temp"] = 30.0  # Hot but not extreme

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = hot_response
        mock_get.return_value = mock_response

        # Should be false with default threshold (35°C)
        result = check_weather_condition(
            self.valid_api_key, self.location, "extreme heat"
        )
        self.assertFalse(result)

        # Should be true with custom threshold (25°C)
        result = check_weather_condition(
            self.valid_api_key, self.location, "extreme heat", threshold=25
        )
        self.assertTrue(result)

    @patch("automations.helpers.weather_helper.requests.get")
    def test_check_weather_condition_extreme_cold(self, mock_get):
        """Test extreme cold condition checking."""
        cold_response = self.weather_api_response.copy()
        cold_response["main"]["temp"] = -15.0  # Very cold

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = cold_response
        mock_get.return_value = mock_response

        result = check_weather_condition(
            self.valid_api_key, self.location, "extreme cold"
        )
        self.assertTrue(result)

    @patch("automations.helpers.weather_helper.requests.get")
    def test_check_weather_condition_windy(self, mock_get):
        """Test windy condition checking."""
        windy_response = self.weather_api_response.copy()
        windy_response["wind"]["speed"] = 15.0  # Very windy

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = windy_response
        mock_get.return_value = mock_response

        result = check_weather_condition(self.valid_api_key, self.location, "windy")
        self.assertTrue(result)

    @patch("automations.helpers.weather_helper.requests.get")
    def test_check_weather_condition_unknown(self, mock_get):
        """Test unknown condition checking."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.weather_api_response
        mock_get.return_value = mock_response

        result = check_weather_condition(
            self.valid_api_key, self.location, "unknown_condition"
        )
        self.assertFalse(result)

    @patch("automations.helpers.weather_helper.requests.get")
    def test_check_weather_condition_api_error(self, mock_get):
        """Test condition checking with API error."""
        mock_get.side_effect = Exception("API Error")

        result = check_weather_condition(self.valid_api_key, self.location, "rain")
        self.assertFalse(result)

    def test_format_weather_message(self):
        """Test weather message formatting."""
        weather_data = {
            "location": "Paris,FR",
            "temperature": 20.5,
            "humidity": 65,
            "description": "clear sky",
            "units": "metric",
        }

        result = format_weather_message(weather_data)
        expected = "Weather in Paris,FR: 20.5°C, clear sky. Humidity: 65%"
        self.assertEqual(result, expected)

    def test_format_weather_message_imperial(self):
        """Test weather message formatting with imperial units."""
        weather_data = {
            "location": "New York,NY",
            "temperature": 68.0,
            "humidity": 50,
            "description": "partly cloudy",
            "units": "imperial",
        }

        result = format_weather_message(weather_data)
        expected = "Weather in New York,NY: 68.0°F, partly cloudy. Humidity: 50%"
        self.assertEqual(result, expected)

    def test_format_weather_message_missing_data(self):
        """Test weather message formatting with missing data."""
        weather_data = {
            "location": "Unknown",
            "temperature": None,
            "humidity": None,
            "description": None,
            "units": "metric",
        }

        result = format_weather_message(weather_data)
        expected = "Weather in Unknown: N/A°C, Unknown. Humidity: N/A%"
        self.assertEqual(result, expected)

    def test_format_weather_message_not_implemented(self):
        """Test weather message formatting for not implemented status."""
        weather_data = {"status": "not_implemented"}

        result = format_weather_message(weather_data)
        self.assertEqual(result, "Weather integration not yet configured")

    @patch("automations.helpers.weather_helper.cached_weather")
    def test_get_weather_data_cached(self, mock_cached_weather):
        """Test cached weather data retrieval."""
        mock_cached_weather.return_value = {
            "location": self.location,
            "temperature": 20.5,
            "description": "clear sky",
        }

        result = get_weather_data_cached(self.valid_api_key, self.location)

        # Verify cache function was called
        mock_cached_weather.assert_called_once()
        self.assertEqual(result["location"], self.location)
        self.assertEqual(result["temperature"], 20.5)

    @patch("automations.helpers.weather_helper.requests.get")
    def test_get_weather_alerts_not_implemented(self, mock_get):
        """Test weather alerts (not yet implemented)."""
        from automations.helpers.weather_helper import get_weather_alerts

        result = get_weather_alerts(self.valid_api_key, self.location)
        self.assertEqual(result, [])

        # Verify no API calls were made
        mock_get.assert_not_called()

    @patch("automations.helpers.weather_helper.logger")
    @patch("automations.helpers.weather_helper.requests.get")
    def test_logging_on_success(self, mock_get, mock_logger):
        """Test that successful API calls are logged."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.weather_api_response
        mock_get.return_value = mock_response

        get_weather_data(self.valid_api_key, self.location)

        # Verify info logging was called
        mock_logger.info.assert_called_once()
        log_call = mock_logger.info.call_args[0][0]
        self.assertIn("Retrieved weather for", log_call)
        self.assertIn(self.location, log_call)

    @patch("automations.helpers.weather_helper.logger")
    @patch("automations.helpers.weather_helper.requests.get")
    def test_logging_on_error(self, mock_get, mock_logger):
        """Test that API errors are logged."""
        from requests.exceptions import RequestException

        mock_get.side_effect = RequestException("API Error")

        with self.assertRaises(RequestException):
            get_weather_data(self.valid_api_key, self.location)

        # Verify error logging was called
        mock_logger.error.assert_called_once()
        log_call = mock_logger.error.call_args[0][0]
        self.assertIn("Weather API failed for", log_call)
        self.assertIn(self.location, log_call)
        self.assertIn("API Error", log_call)
