"""
Main recommendation engine
Handles filtering and scoring of attractions
"""

from typing import List, Dict

from .scoring import ScoreCalculator


class TourismRecommender:
    """Main recommendation engine for tourism attractions."""

    def __init__(self, attractions: List[Dict]) -> None:
        """
        Initialize TourismRecommender.

        Args:
            attractions: List of attraction dictionaries.
        """
        self.attractions = attractions
        self.max_review_count = max([a['review_count'] for a in attractions]) if attractions else 1
        self.max_rating = max([a['rating'] for a in attractions]) if attractions else 5.0
        self.score_calculator = ScoreCalculator(self.max_review_count, self.max_rating)

    def apply_diversity_penalty(self, scored_attractions: List[Dict]) -> List[Dict]:
        """
        Apply diversity penalty so the list is not dominated by one category.

        Progressive penalty per category:
        1st occurrence = 0%, 2nd = 5%, 3rd = 10%, 4th = 15%, etc.
        """
        if len(scored_attractions) < 5:
            return scored_attractions

        category_counts: Dict[str, int] = {}

        for att in scored_attractions:
            categories = att.get('categories', []) or []
            for category in categories:
                cat_lower = str(category).lower()
                count = category_counts.get(cat_lower, 0)
                penalty_percent = count * 5
                if penalty_percent > 0:
                    penalty = (penalty_percent / 100.0) * att['score']
                    att['score'] = max(0.0, att['score'] - penalty)
                category_counts[cat_lower] = count + 1

        scored_attractions.sort(key=lambda x: x['score'], reverse=True)
        return scored_attractions

    def get_recommendations(self, preferences: Dict, limit: int = 10) -> List[Dict]:
        """
        Get top N attractions based on user preferences.

        Filters by:
        - City/country (optional)
        - Categories/interests
        - Minimum rating
        Then applies a diversity penalty before returning results.
        """
        scored_attractions: List[Dict] = []

        for att in self.attractions:
            if preferences.get('city') and preferences['city'] != 'any':
                if att['city'].lower() != str(preferences['city']).lower():
                    continue

            if preferences.get('country') and preferences['country'] != 'any':
                if att['country'].lower() != str(preferences['country']).lower():
                    continue

            score = self.score_calculator.calculate_score(att, preferences)

            if score > 0:
                att_copy: Dict = {
                    'id': att['id'],
                    'place_name': att['place_name'],
                    'city': att['city'],
                    'country': att['country'],
                    'rating': float(att['rating']),
                    'review_count': int(att['review_count']),
                    'categories': att['categories_list'],
                    'categories_display': att['categories'],
                    'score': round(score, 2),
                    'score_breakdown': self.score_calculator.get_score_breakdown(att, preferences),
                }
                scored_attractions.append(att_copy)

        scored_attractions.sort(key=lambda x: x['score'], reverse=True)
        scored_attractions = self.apply_diversity_penalty(scored_attractions)

        return scored_attractions[:limit]
