"""
Configuration file for Tourism Recommendation System
Contains all configurable weights and settings
"""

import os

SCORING_WEIGHTS = {
    "rating_weight": 40,
    "review_weight": 20,
    "city_bonus": 25,
    "country_bonus": 15,
    "category_bonus": 10,
    "perfect_match_bonus": 5,
    "high_rating_bonus": 10,
    "mid_rating_bonus": 5,
    "very_popular_bonus": 10,
    "popular_bonus": 5
}

CACHE_CONFIG = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}

API_CONFIG = {
    "NOMINATIM_BASE_URL": "https://nominatim.openstreetmap.org/search",
    "WEATHER_BASE_URL": "https://api.open-meteo.com/v1/forecast",
    "NOMINATIM_USER_AGENT": "TourismRecommenderApp/1.0",
    "REQUEST_TIMEOUT": 10,
    "NOMINATIM_RATE_LIMIT": 1.0
}

CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'tripadvisor_data.csv')
