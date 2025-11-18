# Tourism Recommendation System

A Python-based tourism recommendation and itinerary optimization system.

## Features

- Smart destination recommendations based on preferences
- Budget-aware itinerary optimization
- Interest-based scoring algorithm
- Beautiful web interface

## Setup

1. Install dependencies: `pip install -r requirements.txt`

2. Run the application: `python app.py`

3. Open browser: `http://localhost:5000`

## How to Use

1. Select your preferences (budget, type, season, interests)

2. Get personalized recommendations

3. Add destinations to your itinerary

4. Optimize your travel plan with days and budget

## Scoring Algorithm

- Base score from destination rating
- +20 points for budget match
- +15 points for type match
- +10 points for season match
- +15 points per matching interest

