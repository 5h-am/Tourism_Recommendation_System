from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import json
from math import log10

app = Flask(__name__)

# Load and process TripAdvisor dataset
CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'tripadvisor_data.csv')

def load_and_process_data():
    """Load CSV data and process it for use in recommendations"""
    try:
        df = pd.read_csv(CSV_PATH)
        
        # Handle missing values
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
        df['review_count'] = pd.to_numeric(df['review_count'], errors='coerce').fillna(0)
        df['place_name'] = df['place_name'].fillna('Unknown')
        df['city'] = df['city'].fillna('Unknown')
        df['country'] = df['country'].fillna('Unknown')
        df['categories'] = df['categories'].fillna('')
        
        # Convert categories string to list
        df['categories_list'] = df['categories'].apply(
            lambda x: [cat.strip() for cat in str(x).split(',') if cat.strip()] if pd.notna(x) and str(x).strip() else []
        )
        
        # Add ID column
        df['id'] = range(1, len(df) + 1)
        
        # Filter out invalid entries
        df = df[(df['rating'] > 0) & (df['review_count'] > 0)]
        
        # Convert to list of dictionaries
        attractions = df.to_dict('records')
        
        # Standardize category names (remove duplicates, normalize)
        for att in attractions:
            att['categories_list'] = list(set([cat.lower().strip() for cat in att['categories_list']]))
            att['categories'] = ', '.join(att['categories_list'])
        
        return attractions, df
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return [], pd.DataFrame()

# Load data on startup
attractions_data, df_data = load_and_process_data()

class TourismRecommender:
    def __init__(self, attractions):
        self.attractions = attractions
        self.max_review_count = max([a['review_count'] for a in attractions]) if attractions else 1
        self.max_rating = max([a['rating'] for a in attractions]) if attractions else 5.0
        
    def calculate_score(self, attraction, preferences):
        """
        Calculate recommendation score for an attraction based on:
        - Base score: rating × review_count (log-normalized)
        - Location matching (city/country)
        - Category matching
        - Review count threshold (popularity bonus)
        - Rating threshold (quality bonus)
        """
        score = 0.0
        
        # Base score: weighted combination of rating and review_count
        # Normalize review_count using log scale (since it can vary widely)
        normalized_reviews = log10(attraction['review_count'] + 1) / log10(self.max_review_count + 1)
        base_score = (attraction['rating'] / 5.0) * 40 + normalized_reviews * 20
        score += base_score
        
        # Location matching bonus
        if preferences.get('city'):
            if attraction['city'].lower() == str(preferences['city']).lower():
                score += 25
        
        if preferences.get('country'):
            if attraction['country'].lower() == str(preferences['country']).lower():
                score += 15
        
        # Category matching bonus
        if preferences.get('categories') and len(preferences['categories']) > 0:
            attraction_cats = set([cat.lower() for cat in attraction['categories_list']])
            user_cats = set([cat.lower() for cat in preferences['categories']])
            matching_cats = attraction_cats & user_cats
            if matching_cats:
                score += len(matching_cats) * 10
                # Bonus for perfect match
                if len(matching_cats) == len(user_cats):
                    score += 5
        
        # Rating threshold bonus
        min_rating = preferences.get('min_rating', 0)
        if attraction['rating'] >= min_rating:
            if attraction['rating'] >= 4.5:
                score += 10  # High quality bonus
            elif attraction['rating'] >= 4.0:
                score += 5
        else:
            return 0  # Filter out below threshold
        
        # Review count popularity bonus
        if attraction['review_count'] >= 200000:
            score += 10  # Very popular
        elif attraction['review_count'] >= 100000:
            score += 5  # Popular
        
        # Normalize to 0-100 range
        return min(100, max(0, score))
    
    def get_recommendations(self, preferences, limit=10):
        """
        Get top N attractions based on user preferences
        Filters by:
        - City/country (optional)
        - Categories/interests
        - Minimum rating
        Sorts by calculated score
        """
        scored_attractions = []
        
        for att in self.attractions:
            # Apply filters
            if preferences.get('city') and preferences['city'] != 'any':
                if att['city'].lower() != str(preferences['city']).lower():
                    continue
            
            if preferences.get('country') and preferences['country'] != 'any':
                if att['country'].lower() != str(preferences['country']).lower():
                    continue
            
            # Calculate score
            score = self.calculate_score(att, preferences)
            
            if score > 0:  # Only include attractions that pass filters
                att_copy = {
                    'id': att['id'],
                    'place_name': att['place_name'],
                    'city': att['city'],
                    'country': att['country'],
                    'rating': float(att['rating']),
                    'review_count': int(att['review_count']),
                    'categories': att['categories_list'],
                    'categories_display': att['categories'],
                    'score': round(score, 2),
                    'score_breakdown': self._get_score_breakdown(att, preferences)
                }
                scored_attractions.append(att_copy)
        
        # Sort by score (descending)
        scored_attractions.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_attractions[:limit]
    
    def _get_score_breakdown(self, attraction, preferences):
        """Get breakdown of score calculation for transparency"""
        breakdown = {
            'base_score': round((attraction['rating'] / 5.0) * 40 + 
                               (log10(attraction['review_count'] + 1) / log10(self.max_review_count + 1)) * 20, 2),
            'location_bonus': 0,
            'category_bonus': 0,
            'quality_bonus': 0,
            'popularity_bonus': 0
        }
        
        # Location bonus
        if preferences.get('city') and attraction['city'].lower() == str(preferences['city']).lower():
            breakdown['location_bonus'] += 25
        if preferences.get('country') and attraction['country'].lower() == str(preferences['country']).lower():
            breakdown['location_bonus'] += 15
        
        # Category bonus
        if preferences.get('categories'):
            attraction_cats = set([cat.lower() for cat in attraction['categories_list']])
            user_cats = set([cat.lower() for cat in preferences['categories']])
            matching_cats = attraction_cats & user_cats
            if matching_cats:
                breakdown['category_bonus'] = len(matching_cats) * 10 + (5 if len(matching_cats) == len(user_cats) else 0)
        
        # Quality and popularity bonuses
        if attraction['rating'] >= 4.5:
            breakdown['quality_bonus'] = 10
        elif attraction['rating'] >= 4.0:
            breakdown['quality_bonus'] = 5
        
        if attraction['review_count'] >= 200000:
            breakdown['popularity_bonus'] = 10
        elif attraction['review_count'] >= 100000:
            breakdown['popularity_bonus'] = 5
        
        return breakdown
    
    def optimize_itinerary(self, attraction_ids, total_days):
        """
        Create optimized multi-day itinerary
        - Distribute attractions across days
        - Group by city to minimize travel
        - Estimate time per attraction based on category
        """
        selected_attractions = [a for a in self.attractions if a['id'] in attraction_ids]
        
        if not selected_attractions:
            return {"error": "No attractions selected"}
        
        if total_days <= 0:
            return {"error": "Invalid number of days"}
        
        # Group attractions by city
        city_groups = {}
        for att in selected_attractions:
            city = att['city']
            if city not in city_groups:
                city_groups[city] = []
            city_groups[city].append(att)
        
        # Estimate time per attraction based on categories
        def estimate_time(att):
            categories = [cat.lower() for cat in att['categories_list']]
            if 'museums' in categories or 'parks' in categories or 'ruins' in categories:
                return 3  # 3 hours for museums, parks, ruins
            elif 'beaches' in categories or 'nature' in categories:
                return 2  # 2 hours for beaches, nature
            elif 'temples' in categories or 'churches' in categories:
                return 1.5  # 1.5 hours for religious sites
            elif 'shopping' in categories or 'markets' in categories:
                return 2  # 2 hours for shopping
            else:
                return 2  # Default 2 hours
        
        # Prepare all attractions with estimated times
        all_attractions_with_time = []
        for att in selected_attractions:
            time_needed = estimate_time(att)
            all_attractions_with_time.append({
                'id': att['id'],
                'name': att['place_name'],
                'city': att['city'],
                'country': att['country'],
                'rating': float(att['rating']),
                'review_count': int(att['review_count']),
                'categories': att['categories_list'],
                'estimated_time': time_needed
            })
        
        # Distribute attractions across days
        # Aim for 6-8 hours of activities per day, group by city when possible
        itinerary = []
        max_hours_per_day = 8
        min_hours_per_day = 4
        
        # Calculate total hours needed
        total_hours = sum(att['estimated_time'] for att in all_attractions_with_time)
        avg_hours_per_day = total_hours / total_days
        
        # Group attractions by city first (try to keep same city on same day)
        current_day = 1
        daily_attractions = []
        daily_hours = 0
        daily_cities = set()
        
        # Sort by city to group them together
        all_attractions_with_time.sort(key=lambda x: x['city'])
        
        for att in all_attractions_with_time:
            time_needed = att['estimated_time']
            
            # Check if we should start a new day
            should_new_day = False
            
            # New day if we exceed max hours
            if daily_hours + time_needed > max_hours_per_day and daily_attractions:
                should_new_day = True
            # New day if we're at target and have enough attractions
            elif current_day < total_days and daily_hours >= avg_hours_per_day and daily_attractions:
                # Check if this is a different city and we have enough content for current day
                if att['city'] not in daily_cities and daily_hours >= min_hours_per_day:
                    should_new_day = True
            
            if should_new_day and current_day < total_days:
                # Save current day
                itinerary.append({
                    'day': current_day,
                    'attractions': daily_attractions.copy(),
                    'cities': list(daily_cities),
                    'total_hours': round(daily_hours, 1),
                    'total_attractions': len(daily_attractions)
                })
                current_day += 1
                daily_attractions = []
                daily_hours = 0
                daily_cities = set()
            
            # Add attraction to current day
            daily_attractions.append(att)
            daily_hours += time_needed
            daily_cities.add(att['city'])
        
        # Add last day (or remaining attractions)
        if daily_attractions:
            itinerary.append({
                'day': current_day,
                'attractions': daily_attractions,
                'cities': list(daily_cities),
                'total_hours': round(daily_hours, 1),
                'total_attractions': len(daily_attractions)
            })
        
        # If we have fewer days used than requested, we're done
        # If we have more days than requested, the user needs more days or fewer attractions
        # For now, we'll just return what we have
        
        return {
            'itinerary': itinerary,
            'total_days': total_days,
            'total_attractions': len(selected_attractions),
            'cities_visited': list(city_groups.keys())
        }

# Initialize recommender
recommender = TourismRecommender(attractions_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        preferences = request.json or {}
        
        # Get limit from preferences or default to 10
        limit = preferences.get('limit', 10)
        limit = min(max(1, int(limit)), 20)  # Clamp between 1 and 20
        
        recommendations = recommender.get_recommendations(preferences, limit=limit)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/optimize', methods=['POST'])
def optimize():
    try:
        data = request.json or {}
        attraction_ids = data.get('attractionIds', [])
        total_days = data.get('days', 0)
        
        result = recommender.optimize_itinerary(attraction_ids, total_days)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/destinations', methods=['GET'])
def get_destinations():
    """Get all unique cities and countries"""
    try:
        if df_data.empty:
            return jsonify({'cities': [], 'countries': []})
        
        cities = sorted(df_data['city'].dropna().unique().tolist())
        countries = sorted(df_data['country'].dropna().unique().tolist())
        
        return jsonify({
            'cities': cities,
            'countries': countries
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all unique categories from the dataset"""
    try:
        all_categories = set()
        for att in attractions_data:
            all_categories.update(att['categories_list'])
        
        categories = sorted([cat.title() for cat in all_categories if cat])
        return jsonify({'categories': categories})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print(f"Loaded {len(attractions_data)} attractions from dataset")
    app.run(debug=True, port=5000)
