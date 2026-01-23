"""
Scoring logic for tourism recommendations
Handles calculation of recommendation scores with configurable weights
"""

from math import log10
from typing import Dict, List
from config import SCORING_WEIGHTS


class ScoreCalculator:
    """Calculates recommendation scores based on configurable weights"""
    
    def __init__(self, max_review_count: float, max_rating: float = 5.0):
        """
        Initialize ScoreCalculator
        
        Args:
            max_review_count: Maximum review count for normalization
            max_rating: Maximum rating (default 5.0)
        """
        self.max_review_count = max_review_count
        self.max_rating = max_rating
        self.weights = SCORING_WEIGHTS
    
    def calculate_score(self, attraction: Dict, preferences: Dict) -> float:
        """
        Calculate recommendation score for an attraction based on:
        - Base score: rating × review_count (log-normalized)
        - Location matching (city/country)
        - Category matching
        - Review count threshold (popularity bonus)
        - Rating threshold (quality bonus)
        
        Args:
            attraction: Attraction dictionary
            preferences: User preferences dictionary
            
        Returns:
            Score between 0-100
        """
        score = 0.0
        
        normalized_reviews = log10(attraction['review_count'] + 1) / log10(self.max_review_count + 1)
        base_score = (attraction['rating'] / self.max_rating) * self.weights['rating_weight'] + \
                     normalized_reviews * self.weights['review_weight']
        score += base_score
        
        if preferences.get('city'):
            if attraction['city'].lower() == str(preferences['city']).lower():
                score += self.weights['city_bonus']
        
        if preferences.get('country'):
            if attraction['country'].lower() == str(preferences['country']).lower():
                score += self.weights['country_bonus']
        
        if preferences.get('categories') and len(preferences['categories']) > 0:
            attraction_cats = set([cat.lower() for cat in attraction['categories_list']])
            user_cats = set([cat.lower() for cat in preferences['categories']])
            matching_cats = attraction_cats & user_cats
            if matching_cats:
                score += len(matching_cats) * self.weights['category_bonus']
                if len(matching_cats) == len(user_cats):
                    score += self.weights['perfect_match_bonus']
        
        min_rating = preferences.get('min_rating', 0)
        if attraction['rating'] >= min_rating:
            if attraction['rating'] >= 4.5:
                score += self.weights['high_rating_bonus']
            elif attraction['rating'] >= 4.0:
                score += self.weights['mid_rating_bonus']
        else:
            return 0
        
        if attraction['review_count'] >= 200000:
            score += self.weights['very_popular_bonus']
        elif attraction['review_count'] >= 100000:
            score += self.weights['popular_bonus']
        
        return min(100, max(0, score))
    
    def get_score_breakdown(self, attraction: Dict, preferences: Dict) -> Dict:
        """
        Get breakdown of score calculation for transparency
        
        Args:
            attraction: Attraction dictionary
            preferences: User preferences dictionary
            
        Returns:
            Dictionary with score breakdown components
        """
        breakdown = {
            'base_score': round(
                (attraction['rating'] / self.max_rating) * self.weights['rating_weight'] + 
                (log10(attraction['review_count'] + 1) / log10(self.max_review_count + 1)) * 
                self.weights['review_weight'], 
                2
            ),
            'location_bonus': 0,
            'category_bonus': 0,
            'quality_bonus': 0,
            'popularity_bonus': 0
        }
        
        if preferences.get('city') and attraction['city'].lower() == str(preferences['city']).lower():
            breakdown['location_bonus'] += self.weights['city_bonus']
        if preferences.get('country') and attraction['country'].lower() == str(preferences['country']).lower():
            breakdown['location_bonus'] += self.weights['country_bonus']
        
        if preferences.get('categories'):
            attraction_cats = set([cat.lower() for cat in attraction['categories_list']])
            user_cats = set([cat.lower() for cat in preferences['categories']])
            matching_cats = attraction_cats & user_cats
            if matching_cats:
                breakdown['category_bonus'] = len(matching_cats) * self.weights['category_bonus'] + \
                    (self.weights['perfect_match_bonus'] if len(matching_cats) == len(user_cats) else 0)
        
        if attraction['rating'] >= 4.5:
            breakdown['quality_bonus'] = self.weights['high_rating_bonus']
        elif attraction['rating'] >= 4.0:
            breakdown['quality_bonus'] = self.weights['mid_rating_bonus']
        
        if attraction['review_count'] >= 200000:
            breakdown['popularity_bonus'] = self.weights['very_popular_bonus']
        elif attraction['review_count'] >= 100000:
            breakdown['popularity_bonus'] = self.weights['popular_bonus']
        
        return breakdown
