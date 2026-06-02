from fastapi import FastAPI, HTTPException
from backend.models import UserPreferences, RecommendationResponse
from backend.orchestrator import RecommendationOrchestrator

app = FastAPI(
    title="Zomato AI Recommendation API", 
    description="REST API backend for AI-powered restaurant recommendations",
    version="1.0.0"
)

# Initialize Orchestrator
orchestrator = RecommendationOrchestrator()

@app.on_event("startup")
def startup_event():
    # Pre-load Zomato dataset cache on startup to avoid delay on first request
    print("API: Pre-loading Zomato dataset...")
    orchestrator.load_dataset()
    print("API: Dataset pre-loaded successfully.")

@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy", 
        "service": "zomato-ai-recommender-api",
        "loaded_records": len(orchestrator.df) if orchestrator.df is not None else 0
    }

@app.post("/api/v1/recommendations", response_model=RecommendationResponse)
def get_recommendations(preferences: UserPreferences):
    """
    Generate personalized recommendations based on location, cuisine, budget, rating, 
    and custom AI explanations.
    """
    try:
        response = orchestrator.recommend(preferences)
        return response
    except Exception as e:
        print(f"API Error during recommendation pipeline: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred in the recommendation pipeline: {str(e)}"
        )
