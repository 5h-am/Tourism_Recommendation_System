from flask import Flask, render_template, request, jsonify

import json

from datetime import datetime



app = Flask(__name__)



# Sample tourism data

destinations = [

    {"id": 1, "name": "Paris", "country": "France", "type": "city", "budget": "high", 

     "interests": ["culture", "food", "art"], "rating": 4.8, "season": ["spring", "fall"],

     "description": "City of Light and Romance"},

    {"id": 2, "name": "Bali", "country": "Indonesia", "type": "beach", "budget": "medium",

     "interests": ["beach", "nature", "wellness"], "rating": 4.7, "season": ["summer", "spring"],

     "description": "Tropical paradise with rich culture"},

    {"id": 3, "name": "Tokyo", "country": "Japan", "type": "city", "budget": "high",

     "interests": ["culture", "food", "technology"], "rating": 4.9, "season": ["spring", "fall"],

     "description": "Modern metropolis meets tradition"},

    {"id": 4, "name": "Barcelona", "country": "Spain", "type": "city", "budget": "medium",

     "interests": ["culture", "beach", "food"], "rating": 4.6, "season": ["summer", "spring"],

     "description": "Vibrant city with stunning architecture"},

    {"id": 5, "name": "Maldives", "country": "Maldives", "type": "beach", "budget": "high",

     "interests": ["beach", "luxury", "diving"], "rating": 4.9, "season": ["winter", "spring"],

     "description": "Ultimate luxury beach destination"},

    {"id": 6, "name": "Prague", "country": "Czech Republic", "type": "city", "budget": "low",

     "interests": ["culture", "history", "architecture"], "rating": 4.7, "season": ["spring", "fall"],

     "description": "Medieval charm and Gothic beauty"},

    {"id": 7, "name": "Thailand", "country": "Thailand", "type": "mixed", "budget": "low",

     "interests": ["beach", "culture", "food"], "rating": 4.8, "season": ["winter", "spring"],

     "description": "Land of smiles and diverse experiences"},

    {"id": 8, "name": "New York", "country": "USA", "type": "city", "budget": "high",

     "interests": ["culture", "food", "shopping"], "rating": 4.7, "season": ["fall", "spring"],

     "description": "The city that never sleeps"},

    {"id": 9, "name": "Iceland", "country": "Iceland", "type": "nature", "budget": "high",

     "interests": ["nature", "adventure", "photography"], "rating": 4.8, "season": ["summer", "winter"],

     "description": "Land of fire and ice"},

    {"id": 10, "name": "Costa Rica", "country": "Costa Rica", "type": "nature", "budget": "medium",

     "interests": ["nature", "adventure", "wildlife"], "rating": 4.7, "season": ["winter", "spring"],

     "description": "Eco-tourism paradise"}

]



class TourismRecommender:

    def __init__(self, destinations_data):

        self.destinations = destinations_data

    

    def calculate_score(self, destination, preferences):

        score = destination['rating'] * 10

        

        # Budget matching

        if preferences.get('budget') and destination['budget'] == preferences['budget']:

            score += 20

        

        # Type matching

        if preferences.get('type') and destination['type'] == preferences['type']:

            score += 15

        

        # Season matching

        if preferences.get('season') and preferences['season'] in destination['season']:

            score += 10

        

        # Interests matching

        if preferences.get('interests'):

            matching_interests = set(preferences['interests']) & set(destination['interests'])

            score += len(matching_interests) * 15

        

        return score

    

    def get_recommendations(self, preferences, limit=5):

        scored_destinations = []

        

        for dest in self.destinations:

            score = self.calculate_score(dest, preferences)

            dest_copy = dest.copy()

            dest_copy['score'] = round(score, 2)

            scored_destinations.append(dest_copy)

        

        # Sort by score in descending order

        scored_destinations.sort(key=lambda x: x['score'], reverse=True)

        

        return scored_destinations[:limit]

    

    def optimize_itinerary(self, destination_ids, total_days, budget=None):

        selected_destinations = [d for d in self.destinations if d['id'] in destination_ids]

        

        if not selected_destinations:

            return {"error": "No destinations selected"}

        

        days_per_destination = total_days // len(selected_destinations)

        remaining_days = total_days % len(selected_destinations)

        

        itinerary = []

        total_cost = 0

        current_day = 1

        

        # Cost per day based on budget level

        cost_mapping = {'low': 80, 'medium': 150, 'high': 250}

        

        for i, dest in enumerate(selected_destinations):

            days = days_per_destination + (1 if i < remaining_days else 0)

            daily_cost = cost_mapping[dest['budget']]

            destination_cost = days * daily_cost

            

            itinerary.append({

                'destination': dest['name'],

                'country': dest['country'],

                'days': days,

                'start_day': current_day,

                'end_day': current_day + days - 1,

                'estimated_cost': destination_cost,

                'activities': dest['interests'][:3],

                'budget_level': dest['budget']

            })

            

            total_cost += destination_cost

            current_day += days

        

        return {

            'itinerary': itinerary,

            'total_days': total_days,

            'total_cost': total_cost,

            'within_budget': budget is None or total_cost <= budget,

            'average_daily_cost': round(total_cost / total_days, 2)

        }



recommender = TourismRecommender(destinations)



@app.route('/')

def index():

    return render_template('index.html')



@app.route('/api/recommend', methods=['POST'])

def recommend():

    preferences = request.json

    recommendations = recommender.get_recommendations(preferences)

    return jsonify(recommendations)



@app.route('/api/optimize', methods=['POST'])

def optimize():

    data = request.json

    destination_ids = data.get('destinationIds', [])

    days = data.get('days', 0)

    budget = data.get('budget')

    

    result = recommender.optimize_itinerary(destination_ids, days, budget)

    return jsonify(result)



@app.route('/api/destinations', methods=['GET'])

def get_destinations():

    return jsonify(destinations)



if __name__ == '__main__':

    app.run(debug=True, port=5000)

