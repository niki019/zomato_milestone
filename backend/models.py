from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict

class Restaurant(BaseModel):
    id: str
    name: str
    location: str
    cuisines: List[str]
    rating: float
    estimated_cost: float
    budget_band: Literal["low", "medium", "high"]
    metadata: Optional[Dict] = Field(default_factory=dict)

class UserPreferences(BaseModel):
    state: str
    city: str
    location: str  # representing local area / neighborhood
    budget: Literal["low", "medium", "high"]
    cuisine: str
    min_rating: float = Field(default=3.5, ge=0.0, le=5.0)
    additional_preferences: Optional[str] = None
    top_k: int = Field(default=5, ge=1)

class Recommendation(BaseModel):
    restaurant: Restaurant
    rank: int
    explanation: str

class RecommendationResponse(BaseModel):
    summary: Optional[str] = None
    recommendations: List[Recommendation]
