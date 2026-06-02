import os
import pandas as pd
from dotenv import load_dotenv

# Load env variables from the root .env file if it exists
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

class FilterEngine:
    def __init__(self, budget_bounds=None):
        """
        Initializes the filter engine.
        budget_bounds defines:
          - 'low': <= bound1
          - 'medium': bound1 < cost <= bound2
          - 'high': > bound2
        """
        if budget_bounds is None:
            # Check env for custom limits, fallback to Zomato standard values
            low_max = float(os.getenv("BUDGET_LOW_MAX", "400.0"))
            medium_max = float(os.getenv("BUDGET_MEDIUM_MAX", "1000.0"))
            self.budget_bounds = {
                'low': low_max,
                'medium_upper': medium_max
            }
        else:
            self.budget_bounds = budget_bounds


    def apply_filters(self, df: pd.DataFrame, location: str = None, 
                      budget: str = None, cuisine: str = None, 
                      min_rating: float = None, limit: int = 15) -> pd.DataFrame:
        """
        Filters the dataframe based on input parameters.
        Returns a sorted, limited DataFrame of matching candidates.
        """
        filtered_df = df.copy()

        # 1. Filter by location (Case-insensitive match)
        if location and isinstance(location, str) and location.strip():
            loc_query = location.strip().lower()
            filtered_df = filtered_df[filtered_df['location'].str.lower().str.contains(loc_query, na=False)]

        # 2. Filter by cuisine (Case-insensitive match)
        if cuisine and isinstance(cuisine, str) and cuisine.strip():
            cui_query = cuisine.strip().lower()
            # In Zomato dataset, 'cuisines' is a comma-separated list of items
            filtered_df = filtered_df[filtered_df['cuisines'].str.lower().str.contains(cui_query, na=False)]

        # 3. Filter by rating
        if min_rating is not None:
            try:
                min_r = float(min_rating)
                filtered_df = filtered_df[filtered_df['rating'] >= min_r]
            except ValueError:
                pass

        # 4. Filter by budget
        if budget and isinstance(budget, str) and budget.strip():
            b_level = budget.strip().lower()
            low_bound = self.budget_bounds['low']
            med_upper = self.budget_bounds['medium_upper']
            
            if b_level == 'low':
                filtered_df = filtered_df[filtered_df['approx_cost'] <= low_bound]
            elif b_level == 'medium':
                filtered_df = filtered_df[
                    (filtered_df['approx_cost'] > low_bound) & 
                    (filtered_df['approx_cost'] <= med_upper)
                ]
            elif b_level == 'high':
                filtered_df = filtered_df[filtered_df['approx_cost'] > med_upper]

        # Edge Case: If zero results matched, try relaxing filters (e.g. relax rating first, then budget)
        if filtered_df.empty:
            print("No exact matches found. Attempting to relax filters...")
            # We relax by dropping rating filter first, then budget filter, but keeping location & cuisine if possible
            relaxed_df = df.copy()
            
            # Keep location
            if location and isinstance(location, str) and location.strip():
                loc_query = location.strip().lower()
                relaxed_df = relaxed_df[relaxed_df['location'].str.lower().str.contains(loc_query, na=False)]
            
            # Keep cuisine
            if cuisine and isinstance(cuisine, str) and cuisine.strip():
                cui_query = cuisine.strip().lower()
                relaxed_df = relaxed_df[relaxed_df['cuisines'].str.lower().str.contains(cui_query, na=False)]
                
            if not relaxed_df.empty:
                filtered_df = relaxed_df
                print("Filter relaxed: Dropped rating and budget constraints.")

        # Sort by rating (highest first) and then by approx cost (lower cost first for same rating)
        filtered_df = filtered_df.sort_values(by=['rating', 'approx_cost'], ascending=[False, True])

        # Return top N candidates to avoid flooding the LLM context window
        return filtered_df.head(limit)
