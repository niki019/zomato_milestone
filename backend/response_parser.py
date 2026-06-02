import json
import re
from backend.models import Restaurant, Recommendation, RecommendationResponse

def clean_and_parse_json(text: str) -> dict:
    """Strips markdown markers and parses raw text into a dict."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
        cleaned = re.sub(r"\n```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception as e:
        print(f"ResponseParser: Failed to parse raw JSON. Error: {e}. Text: {text}")
        raise e

def parse_response(raw_text: str, candidates: list[Restaurant]) -> RecommendationResponse:
    """
    Parses LLM output, performs grounding verification, 
    and merges it with canonical Restaurant entities.
    """
    candidates_map = {c.id: c for c in candidates}
    
    try:
        data = clean_and_parse_json(raw_text)
        summary = data.get("summary")
        recommendations = []
        
        for idx, item in enumerate(data.get("recommendations", [])):
            r_id = item.get("restaurant_id")
            
            if not candidates:
                # Generative Mode: No candidate database context, construct dynamically from LLM response
                cost = float(item.get("estimated_cost", 500.0))
                budget_band = "medium"
                if cost <= 500.0:
                    budget_band = "low"
                elif cost > 1500.0:
                    budget_band = "high"
                
                cuisines_val = item.get("cuisines", ["Local"])
                if isinstance(cuisines_val, str):
                    cuisines_val = [c.strip() for c in cuisines_val.split(",") if c.strip()]
                    
                rest_obj = Restaurant(
                    id=r_id or f"ext_{idx}",
                    name=item.get("name", "Unknown Restaurant"),
                    location=item.get("location", "Local Area"),
                    cuisines=cuisines_val,
                    rating=float(item.get("rating", 4.0)),
                    estimated_cost=cost,
                    budget_band=budget_band
                )
                rec_obj = Recommendation(
                    restaurant=rest_obj,
                    rank=item.get("rank", len(recommendations) + 1),
                    explanation=item.get("explanation", "Matches your preferences.")
                )
                recommendations.append(rec_obj)
            
            # Grounding check: Ensure returned ID exists in our candidate set
            elif r_id in candidates_map:
                rec_obj = Recommendation(
                    restaurant=candidates_map[r_id],
                    rank=item.get("rank", len(recommendations) + 1),
                    explanation=item.get("explanation", "Matches your preferences.")
                )
                recommendations.append(rec_obj)
            else:
                print(f"ResponseParser Warning: LLM suggested restaurant ID '{r_id}' which was not in candidates list. Dropping.")
                
        # If successfully parsed but no valid recommendations, raise exception to trigger fallback
        if not recommendations:
            raise ValueError("No recommendations parsed.")
            
        return RecommendationResponse(summary=summary, recommendations=recommendations)
        
    except Exception as e:
        print(f"ResponseParser Fallback triggered due to error: {e}")
        return generate_fallback_response(candidates)

def generate_fallback_response(candidates: list[Restaurant], top_k: int = 5) -> RecommendationResponse:
    """
    Fallback ranking: Sort candidates by rating descending 
    and build a structured response without LLM.
    """
    sorted_candidates = sorted(candidates, key=lambda x: x.rating, reverse=True)[:top_k]
    recommendations = []
    for idx, c in enumerate(sorted_candidates):
        rank = idx + 1
        exp = (
            f"Recommended based on its excellent rating of {c.rating}/5. "
            f"Serving {', '.join(c.cuisines)} in {c.location} for around ₹{c.estimated_cost} for two."
        )
        recommendations.append(Recommendation(
            restaurant=c,
            rank=rank,
            explanation=exp
        ))
        
    summary = "Fallback recommendations generated based on historical rating values due to processing delays."
    return RecommendationResponse(summary=summary, recommendations=recommendations)
