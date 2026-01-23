"""
Weather service for fetching current weather data
Uses Open-Meteo API with geocoding integration
"""

import requests
from typing import Optional, Dict
from config import API_CONFIG
from .geocoding_service import GeocodingService


class WeatherService:
    """Service for fetching weather data for cities"""
    
    def __init__(self):
        """Initialize WeatherService with geocoding"""
        self.base_url = API_CONFIG['WEATHER_BASE_URL']
        self.timeout = API_CONFIG['REQUEST_TIMEOUT']
        self.geocoding_service = GeocodingService()
    
    def get_weather(self, city: str, country: str) -> Optional[Dict]:
        """
        Fetch current weather for a city and country
        
        Args:
            city: City name
            country: Country name
            
        Returns:
            Dictionary with weather data or None if error
        """
        if not city or not country:
            return None
        
        try:
            coordinates = self.geocoding_service.get_coordinates(city, country)
            if not coordinates:
                return None
            
            lat, lon = coordinates
            
            params = {
                'latitude': lat,
                'longitude': lon,
                'current_weather': 'true'
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'current_weather' in data:
                weather = data['current_weather']
                return {
                    'temperature': weather.get('temperature', 0),
                    'windspeed': weather.get('windspeed', 0),
                    'weathercode': weather.get('weathercode', 0),
                    'condition': self._get_weather_condition(weather.get('weathercode', 0)),
                    'city': city,
                    'country': country
                }
            
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather for {city}, {country}: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"Error parsing weather data for {city}, {country}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in weather service: {e}")
            return None
    
    def _get_weather_condition(self, weathercode: int) -> str:
        """
        Convert WMO weather code to human-readable condition.
        Uses simplified mapping for common WMO weather interpretation codes.
        
        Args:
            weathercode: WMO weather code
            
        Returns:
            Human-readable weather condition
        """
        if weathercode == 0:
            return "clear"
        elif weathercode in [1, 2, 3]:
            return "partly_cloudy"
        elif weathercode in [45, 48]:
            return "foggy"
        elif weathercode in [51, 53, 55, 56, 57]:
            return "drizzle"
        elif weathercode in [61, 63, 65, 66, 67, 80, 81, 82]:
            return "rain"
        elif weathercode in [71, 73, 75, 77, 85, 86]:
            return "snow"
        elif weathercode in [95, 96, 99]:
            return "thunderstorm"
        else:
            return "unknown"
