import pytest
import pandas as pd
from backend.filter_engine import FilterEngine

@pytest.fixture
def sample_data():
    """Provides a sample DataFrame representing Zomato restaurants."""
    data = [
        {"name": "Pizza Palace", "location": "Banashankari", "cuisines": "Italian, Pizza", "rating": 4.5, "approx_cost": 300.0},
        {"name": "Curry House", "location": "Banashankari", "cuisines": "North Indian, South Indian", "rating": 4.2, "approx_cost": 600.0},
        {"name": "China Town", "location": "Indiranagar", "cuisines": "Chinese", "rating": 3.9, "approx_cost": 800.0},
        {"name": "Spaghetti Corner", "location": "Indiranagar", "cuisines": "Italian, Pasta", "rating": 4.8, "approx_cost": 1200.0},
        {"name": "Five Star Burger", "location": "Whitefield", "cuisines": "Burgers, Fast Food", "rating": 3.5, "approx_cost": 250.0},
        {"name": "Royal Feast", "location": "Whitefield", "cuisines": "North Indian, Mughlai", "rating": 4.6, "approx_cost": 1600.0}
    ]
    return pd.DataFrame(data)

def test_filter_by_location(sample_data):
    engine = FilterEngine()
    # Exact location match
    res = engine.apply_filters(sample_data, location="Banashankari")
    assert len(res) == 2
    assert all(res['location'] == "Banashankari")

    # Partial / case-insensitive match
    res_partial = engine.apply_filters(sample_data, location="indira")
    assert len(res_partial) == 2
    assert all(res_partial['location'] == "Indiranagar")

def test_filter_by_cuisine(sample_data):
    engine = FilterEngine()
    res = engine.apply_filters(sample_data, cuisine="Italian")
    assert len(res) == 2
    assert "Pizza Palace" in res['name'].values
    assert "Spaghetti Corner" in res['name'].values

def test_filter_by_rating(sample_data):
    engine = FilterEngine()
    res = engine.apply_filters(sample_data, min_rating=4.5)
    assert len(res) == 3
    assert all(res['rating'] >= 4.5)

def test_filter_by_budget(sample_data):
    engine = FilterEngine(budget_bounds={'low': 400.0, 'medium_upper': 1000.0})
    
    # Low budget (<= 400)
    low_res = engine.apply_filters(sample_data, budget="low")
    assert len(low_res) == 2
    assert "Pizza Palace" in low_res['name'].values
    assert "Five Star Burger" in low_res['name'].values

    # Medium budget (400 < cost <= 1000)
    med_res = engine.apply_filters(sample_data, budget="medium")
    assert len(med_res) == 2
    assert "Curry House" in med_res['name'].values
    assert "China Town" in med_res['name'].values

    # High budget (> 1000)
    high_res = engine.apply_filters(sample_data, budget="high")
    assert len(high_res) == 2
    assert "Spaghetti Corner" in high_res['name'].values
    assert "Royal Feast" in high_res['name'].values

def test_filter_relaxation(sample_data):
    # Search that yields 0 exact matches
    # Location = Banashankari, Cuisine = Italian, Rating >= 4.9 (none of Banashankari is >= 4.9)
    engine = FilterEngine()
    
    # This should drop the rating threshold and return all Italian in Banashankari
    res = engine.apply_filters(sample_data, location="Banashankari", cuisine="Italian", min_rating=4.9)
    assert len(res) > 0
    assert "Pizza Palace" in res['name'].values
