"""
Main recommendation engine
Handles filtering and scoring of attractions
"""

from typing import List, Dict
from .scoring import ScoreCalculator


class TourismRecommender:
    """Main recommendation engine for tourism attractions"""
    
    def __init__(self, attractions: List[Dict]):
        """
        Initialize TourismRecommender
        
        Args:
            attractions: List of attraction dictionaries
        """
        self.attractions = attractions
        self.max_review_count = max([a['review_count'] for a in attractions]) if attractions else 1
        self.max_rating = max([a['rating'] for a in attractions]) if attractions else 5.0
        self.score_calculator = ScoreCalculator(self.max_review_count, self.max_rating)
    
    def get_recommendations(self, preferences: Dict, limit: int = 10) -> List[Dict]:
        """
        Get top N attractions based on user preferences
        Filters by:
        - City/country (optional)
        - Categories/interests
        - Minimum rating
        Sorts by calculated score
        
        Args:
            preferences: User preferences dictionary
            limit: Maximum number of recommendations to return
            
        Returns:
            List of scored attraction dictionaries
        """
        scored_attractions = []
        
        for att in self.attractions:
            if preferences.get('city') and preferences['city'] != 'any':
                if att['city'].lower() != str(preferences['city']).lower():
                    continue
            
            if preferences.get('country') and preferences['country'] != 'any':
                if att['country'].lower() != str(preferences['country']).lower():
                    continue
            
            score = self.score_calculator.calculate_score(att, preferences)
            
            if score > 0:
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
                    'score_breakdown': self.score_calculator.get_score_breakdown(att, preferences)
                }
                scored_attractions.append(att_copy)
        
        scored_attractions.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_attractions[:limit]
