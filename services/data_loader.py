"""
Data loading service for CSV processing
Handles loading and preprocessing of TripAdvisor dataset
"""

import pandas as pd
from typing import List, Dict, Tuple
from config import CSV_PATH


class DataLoader:
    """Service for loading and processing CSV data"""
    
    def __init__(self, csv_path: str = CSV_PATH):
        """
        Initialize DataLoader with CSV path
        
        Args:
            csv_path: Path to the CSV file
        """
        self.csv_path = csv_path
    
    def load_and_process_data(self) -> Tuple[List[Dict], pd.DataFrame]:
        """
        Load CSV data and process it for use in recommendations
        
        Returns:
            Tuple of (attractions list, DataFrame)
        """
        try:
            df = pd.read_csv(self.csv_path)
            
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
            df['review_count'] = pd.to_numeric(df['review_count'], errors='coerce').fillna(0)
            df['place_name'] = df['place_name'].fillna('Unknown')
            df['city'] = df['city'].fillna('Unknown')
            df['country'] = df['country'].fillna('Unknown')
            df['categories'] = df['categories'].fillna('')
            
            df['categories_list'] = df['categories'].apply(
                lambda x: [cat.strip() for cat in str(x).split(',') if cat.strip()] 
                if pd.notna(x) and str(x).strip() else []
            )
            
            df['id'] = range(1, len(df) + 1)
            df = df[(df['rating'] > 0) & (df['review_count'] > 0)]
            
            attractions = df.to_dict('records')
            
            for att in attractions:
                att['categories_list'] = list(set([cat.lower().strip() for cat in att['categories_list']]))
                att['categories'] = ', '.join(att['categories_list'])
            
            return attractions, df
        
        except Exception as e:
            print(f"Error loading data: {e}")
            return [], pd.DataFrame()
