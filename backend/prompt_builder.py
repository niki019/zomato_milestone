import json
from backend.models import UserPreferences, Restaurant

def get_system_instruction(is_external: bool = False) -> str:
    if is_external:
        return (
            "You are a sophisticated Zomato restaurant recommendation assistant.\n"
            "Your goal is to suggest the best restaurants in the requested state and city based on user preferences.\n"
            "Since no local database entries were provided for this location, you must recommend real, "
            "well-known restaurants from your own external knowledge.\n"
            "Do NOT recommend fabricated or fake venues. Generate realistic estimated costs and ratings.\n"
            "Return the recommendations in the requested JSON structure, including details like name, cuisines, rating, etc."
        )
    return (
        "You are a sophisticated Zomato restaurant recommendation assistant.\n"
        "Your goal is to suggest the best restaurants from the provided list based on the user's preferences.\n"
        "Grounding Rules:\n"
        "1. You must ONLY recommend restaurants from the candidate list provided in the prompt.\n"
        "2. Do NOT invent or hallucinate any restaurants.\n"
        "3. For each recommended restaurant, you must return its exact 'id' from the candidate list.\n"
        "4. If a restaurant's ID is not in the candidate list, it is invalid."
    )

def build_prompt(preferences: UserPreferences, candidates: list[Restaurant]) -> str:
    if not candidates:
        # Prompt for generative search from LLM's own knowledge when database is empty for that state/city
        prompt = f"""
User Preferences:
- State: {preferences.state}
- City: {preferences.city}
- Neighborhood/Area: {preferences.location}
- Budget Band: {preferences.budget}
- Cuisine: {preferences.cuisine}
- Minimum Rating: {preferences.min_rating}
- Additional Custom Preferences: {preferences.additional_preferences or "None"}

Note: No local database entries match this region.
Please recommend {preferences.top_k} real, well-known restaurants located in {preferences.city}, {preferences.state} matching these preferences.

Output format contract:
You must output strictly a JSON object matching this schema:
{{
  "summary": "Brief summary paragraph...",
  "recommendations": [
    {{
      "restaurant_id": "ext1",
      "rank": 1,
      "name": "Real Restaurant Name",
      "location": "Local area/neighborhood inside the city",
      "cuisines": ["Cuisine1", "Cuisine2"],
      "rating": 4.2,
      "estimated_cost": 800.0,
      "explanation": "Why this fits location, budget, cuisine, and extra preferences."
    }}
  ]
}}
"""
        return prompt

    # Convert candidates to a clean serializable structure
    candidate_data = []
    for c in candidates:
        candidate_data.append({
            "id": c.id,
            "name": c.name,
            "location": c.location,
            "cuisines": ", ".join(c.cuisines),
            "rating": c.rating,
            "approx_cost": c.estimated_cost,
            "budget_band": c.budget_band
        })

    prompt = f"""
User Preferences:
- State: {preferences.state}
- City: {preferences.city}
- Neighborhood/Area: {preferences.location}
- Budget Band: {preferences.budget}
- Cuisine: {preferences.cuisine}
- Minimum Rating: {preferences.min_rating}
- Additional Custom Preferences: {preferences.additional_preferences or "None"}

Candidate Restaurants:
{json.dumps(candidate_data, indent=2)}

Task Instructions:
1. Rank the top {preferences.top_k} restaurants that best match the user preferences.
2. Provide a custom, friendly, and persuasive explanation for each ranked option showing why it matches their preferences (e.g., matching the cuisine, budget, rating, or custom requirements).
3. Provide a brief overall summary paragraph of the selection.

Output format contract:
You must output strictly a JSON object matching this schema:
{{
  "summary": "Brief summary paragraph...",
  "recommendations": [
    {{
      "restaurant_id": "the exact ID string from candidates list",
      "rank": 1,
      "explanation": "Why this fits location, budget, cuisine, and extra preferences."
    }}
  ]
}}
"""
    return prompt
