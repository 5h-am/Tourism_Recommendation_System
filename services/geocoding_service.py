"""
Geocoding service for fetching latitude/longitude coordinates
Uses Nominatim OpenStreetMap API with rate limiting
"""

import time
import requests
from typing import Optional, Dict, Tuple
from config import API_CONFIG


class GeocodingService:
    """Service for geocoding city/country names to coordinates"""
    
    def __init__(self):
        """Initialize GeocodingService with rate limiting"""
        self.base_url = API_CONFIG['NOMINATIM_BASE_URL']
        self.user_agent = API_CONFIG['NOMINATIM_USER_AGENT']
        self.timeout = API_CONFIG['REQUEST_TIMEOUT']
        self.rate_limit = API_CONFIG['NOMINATIM_RATE_LIMIT']
        self.last_request_time = 0
    
    def _rate_limit_check(self) -> None:
        """Enforce Nominatim rate limiting (1 request per second)"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()
    
    def get_coordinates(self, city: str, country: str) -> Optional[Tuple[float, float]]:
        """
        Fetch latitude and longitude for a city and country
        
        Args:
            city: City name
            country: Country name
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        if not city or not country:
            return None
        
        try:
            self._rate_limit_check()
            
            query = f"{city},{country}"
            params = {
                'q': query,
                'format': 'json',
                'limit': 1
            }
            
            headers = {
                'User-Agent': self.user_agent
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                location = data[0]
                lat = float(location.get('lat', 0))
                lon = float(location.get('lon', 0))
                if lat != 0 and lon != 0:
                    return (lat, lon)
            
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching coordinates for {city}, {country}: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"Error parsing coordinates for {city}, {country}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in geocoding: {e}")
            return None
