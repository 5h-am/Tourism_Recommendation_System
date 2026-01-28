"""
Main Flask application for Tourism Recommendation System
Refactored to use modular architecture with caching
"""

import os
import hashlib
import json
from typing import Dict, Tuple

from flask import Flask, render_template, request, jsonify
from flask_caching import Cache
from dotenv import load_dotenv

from services.data_loader import DataLoader
from recommender.engine import TourismRecommender
from recommender.itinerary import ItineraryOptimizer
from services.weather_service import WeatherService
from services.geocoding_service import GeocodingService
from config import CACHE_CONFIG

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config.from_mapping(CACHE_CONFIG)
cache = Cache(app)

data_loader = DataLoader()
attractions_data, df_data = data_loader.load_and_process_data()

recommender = TourismRecommender(attractions_data)
itinerary_optimizer = ItineraryOptimizer(attractions_data)
weather_service = WeatherService()
geocoding_service = GeocodingService()
geocode_cache: Dict[Tuple[str, str], Tuple[float, float]] = {}


@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')


@app.route('/api/recommend', methods=['POST'])
def recommend():
    """
    Get recommendations based on user preferences.
    Cached for 5 minutes using request body hash as cache key.
    """
    try:
        preferences = request.json or {}
        limit = preferences.get('limit', 10)
        limit = min(max(1, int(limit)), 20)

        cache_key = hashlib.md5(json.dumps(preferences, sort_keys=True).encode()).hexdigest()
        cached_result = cache.get(f'recommend_{cache_key}')
        if cached_result is not None:
            return jsonify(cached_result)

        recommendations = recommender.get_recommendations(preferences, limit=limit)

        for rec in recommendations:
            city = rec.get('city')
            country = rec.get('country')
            lat = lon = None
            if city and country:
                cache_key_city = (city, country)
                if cache_key_city in geocode_cache:
                    lat, lon = geocode_cache[cache_key_city]
                else:
                    coords = geocoding_service.get_coordinates(city, country)
                    if coords:
                        geocode_cache[cache_key_city] = coords
                        lat, lon = coords
            rec['latitude'] = lat
            rec['longitude'] = lon

        cache.set(f'recommend_{cache_key}', recommendations, timeout=300)

        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/optimize', methods=['POST'])
def optimize():
    """Optimize itinerary for selected attractions. Not cached."""
    try:
        data = request.json or {}
        attraction_ids = data.get('attractionIds', [])
        total_days = data.get('days', 0)

        if not isinstance(attraction_ids, list):
            return jsonify({'error': 'attractionIds must be a list'}), 400
        if not isinstance(total_days, int) or total_days <= 0:
            return jsonify({'error': 'days must be a positive integer'}), 400

        result = itinerary_optimizer.optimize_itinerary(attraction_ids, total_days)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/destinations', methods=['GET'])
@cache.cached(timeout=600)
def get_destinations():
    """Get all unique cities and countries grouped by country. Cached for 10 minutes."""
    try:
        if df_data.empty:
            return jsonify({'cities': [], 'countries': [], 'citiesByCountry': {}})

        countries = sorted(df_data['country'].dropna().unique().tolist())

        cities_by_country: Dict[str, list] = {}
        for country in countries:
            country_cities = sorted(
                df_data[df_data['country'] == country]['city'].dropna().unique().tolist()
            )
            cities_by_country[country] = country_cities

        all_cities = sorted(df_data['city'].dropna().unique().tolist())

        return jsonify({
            'cities': all_cities,
            'countries': countries,
            'citiesByCountry': cities_by_country
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/categories', methods=['GET'])
@cache.cached(timeout=600)
def get_categories():
    """Get all unique categories from the dataset. Cached for 10 minutes."""
    try:
        all_categories = set()
        for att in attractions_data:
            all_categories.update(att['categories_list'])

        categories = sorted([cat.title() for cat in all_categories if cat])
        return jsonify({'categories': categories})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/weather', methods=['POST'])
def get_weather():
    """Get weather information for a city and country. Not cached."""
    try:
        data = request.json or {}
        city = data.get('city', '').strip()
        country = data.get('country', '').strip()

        if not city or not country:
            return jsonify({'error': 'City and country are required'}), 400

        weather_data = weather_service.get_weather(city, country)

        if weather_data:
            return jsonify(weather_data)
        return jsonify({'error': 'Weather data not available for this location'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/geocode', methods=['POST'])
def geocode():
    """Get coordinates for a city and country."""
    try:
        data = request.json or {}
        city = data.get('city', '').strip()
        country = data.get('country', '').strip()

        if not city or not country:
            return jsonify({'error': 'City and country required'}), 400

        cache_key_city = (city, country)
        if cache_key_city in geocode_cache:
            lat, lon = geocode_cache[cache_key_city]
        else:
            coords = geocoding_service.get_coordinates(city, country)
            if not coords:
                return jsonify({}), 404
            geocode_cache[cache_key_city] = coords
            lat, lon = coords

        return jsonify({'latitude': lat, 'longitude': lon})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.getenv('DEBUG', 'False') == 'True'
    print(f"Loaded {len(attractions_data)} attractions from dataset")
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
