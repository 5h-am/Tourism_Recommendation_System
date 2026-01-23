"""
Itinerary optimization module
Handles multi-day itinerary planning and optimization
"""

from typing import List, Dict, Set


class ItineraryOptimizer:
    """Optimizes multi-day itineraries for selected attractions"""
    
    def __init__(self, attractions: List[Dict]):
        """
        Initialize ItineraryOptimizer
        
        Args:
            attractions: List of all available attractions
        """
        self.attractions = attractions
    
    def optimize_itinerary(self, attraction_ids: List[int], total_days: int) -> Dict:
        """
        Create optimized multi-day itinerary
        - Distribute attractions across days
        - Group by city to minimize travel
        - Estimate time per attraction based on category
        
        Args:
            attraction_ids: List of selected attraction IDs
            total_days: Number of days for the trip
            
        Returns:
            Dictionary with itinerary details
        """
        selected_attractions = [a for a in self.attractions if a['id'] in attraction_ids]
        
        if not selected_attractions:
            return {"error": "No attractions selected"}
        
        if total_days <= 0:
            return {"error": "Invalid number of days"}
        
        city_groups = {}
        for att in selected_attractions:
            city = att['city']
            if city not in city_groups:
                city_groups[city] = []
            city_groups[city].append(att)
        
        def estimate_time(att: Dict) -> float:
            """Estimate time needed for an attraction based on its categories"""
            categories = [cat.lower() for cat in att['categories_list']]
            if 'museums' in categories or 'parks' in categories or 'ruins' in categories:
                return 3
            elif 'beaches' in categories or 'nature' in categories:
                return 2
            elif 'temples' in categories or 'churches' in categories:
                return 1.5
            elif 'shopping' in categories or 'markets' in categories:
                return 2
            else:
                return 2
        
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
        
        itinerary = []
        max_hours_per_day = 8
        min_hours_per_day = 4
        
        total_hours = sum(att['estimated_time'] for att in all_attractions_with_time)
        avg_hours_per_day = total_hours / total_days
        
        current_day = 1
        daily_attractions = []
        daily_hours = 0
        daily_cities: Set[str] = set()
        
        all_attractions_with_time.sort(key=lambda x: x['city'])
        
        for att in all_attractions_with_time:
            time_needed = att['estimated_time']
            should_new_day = False
            
            if daily_hours + time_needed > max_hours_per_day and daily_attractions:
                should_new_day = True
            elif current_day < total_days and daily_hours >= avg_hours_per_day and daily_attractions:
                if att['city'] not in daily_cities and daily_hours >= min_hours_per_day:
                    should_new_day = True
            
            if should_new_day and current_day < total_days:
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
            
            daily_attractions.append(att)
            daily_hours += time_needed
            daily_cities.add(att['city'])
        
        if daily_attractions:
            itinerary.append({
                'day': current_day,
                'attractions': daily_attractions,
                'cities': list(daily_cities),
                'total_hours': round(daily_hours, 1),
                'total_attractions': len(daily_attractions)
            })
        
        return {
            'itinerary': itinerary,
            'total_days': total_days,
            'total_attractions': len(selected_attractions),
            'cities_visited': list(city_groups.keys())
        }
