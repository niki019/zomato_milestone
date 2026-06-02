import os
import re
import pandas as pd
from datasets import load_dataset
from dotenv import load_dotenv

# Load env variables from the root .env file if it exists
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

CACHE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.getenv("DATA_PATH")
if env_path:
    project_root = os.path.dirname(CACHE_DIR)
    CACHE_FILE = os.path.abspath(os.path.join(project_root, env_path))
else:
    CACHE_FILE = os.path.join(CACHE_DIR, "data", "zomato_cache.csv")


def clean_rating(val):
    """
    Cleans the rating value.
    Example: '4.1/5' -> 4.1, 'NEW' -> 0.0, '-' -> 0.0, NaN -> 0.0
    """
    if pd.isna(val):
        return 0.0
    val_str = str(val).strip()
    if val_str == '-' or val_str.upper() == 'NEW':
        return 0.0
    if '/' in val_str:
        val_str = val_str.split('/')[0].strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def clean_cost(val):
    """
    Cleans the approx cost for two people.
    Example: '1,200' -> 1200.0, 'Rs. 450' -> 450.0, NaN -> 0.0
    """
    if pd.isna(val):
        return 0.0
    val_str = str(val).strip().replace(',', '')
    match = re.search(r'\d+', val_str)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return 0.0
    return 0.0

def ingest_data(force_reload=False):
    """
    Loads dataset from local cache if it exists, otherwise downloads it
    from Hugging Face and processes/saves it to cache.
    """
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

    if not force_reload and os.path.exists(CACHE_FILE):
        print(f"Loading data from local cache: {CACHE_FILE}")
        return pd.read_csv(CACHE_FILE)

    print("Fetching dataset from Hugging Face: ManikaSaini/zomato-restaurant-recommendation...")
    try:
        dataset = load_dataset("ManikaSaini/zomato-restaurant-recommendation")
        # HF datasets can contain multiple splits; merge them or pick train
        splits = list(dataset.keys())
        print(f"Dataset loaded. Splits found: {splits}")
        
        # Convert first split to DataFrame
        df = pd.DataFrame(dataset[splits[0]])
    except Exception as e:
        print(f"Failed to load from Hugging Face API: {e}")
        # Try fallback if needed (e.g. CSV loading from some mirror, or raise)
        raise e

    print("Preprocessing data...")
    # Select and rename columns to standardize
    # Standard columns in Zomato: name, rate, location, cuisines, approx_cost(for two people)
    # Let's inspect columns to make sure we support both exact match or close match
    columns_mapping = {
        'name': 'name',
        'rate': 'rating_raw',
        'location': 'location',
        'cuisines': 'cuisines',
        'approx_cost(for two people)': 'cost_raw'
    }
    
    # We filter only the columns we need to save memory and context window
    existing_cols = {col: columns_mapping[col] for col in columns_mapping if col in df.columns}
    df = df[list(existing_cols.keys())].rename(columns=existing_cols)
    
    # Apply cleaning
    if 'rating_raw' in df.columns:
        df['rating'] = df['rating_raw'].apply(clean_rating)
        df.drop(columns=['rating_raw'], inplace=True, errors='ignore')
    else:
        df['rating'] = 0.0

    if 'cost_raw' in df.columns:
        df['approx_cost'] = df['cost_raw'].apply(clean_cost)
        df.drop(columns=['cost_raw'], inplace=True, errors='ignore')
    else:
        df['approx_cost'] = 0.0

    # Ensure location and cuisines are clean string columns
    df['location'] = df['location'].fillna("Unknown").astype(str).str.strip()
    df['cuisines'] = df['cuisines'].fillna("").astype(str).str.strip()
    df['name'] = df['name'].fillna("Unnamed Restaurant").astype(str).str.strip()

    # Drop duplicates by name, location and cuisines to clean data
    df = df.drop_duplicates(subset=['name', 'location', 'cuisines'])

    print(f"Ingestion complete. Shape: {df.shape}. Caching data...")
    df.to_csv(CACHE_FILE, index=False)
    return df

if __name__ == "__main__":
    df = ingest_data(force_reload=True)
    print("Sample processed data:")
    print(df.head())
