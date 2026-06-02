import hashlib
from backend.models import UserPreferences, Restaurant, RecommendationResponse
from backend.ingest import ingest_data
from backend.filter_engine import FilterEngine
from backend.llm_recommender import LLMClient
from backend import prompt_builder
from backend import response_parser

class RecommendationOrchestrator:
    def __init__(self):
        self.filter_engine = FilterEngine()
        self.llm_client = LLMClient()
        self.df = None

    def load_dataset(self):
        """Loads Zomato dataset in memory if not already done."""
        if self.df is None:
            self.df = ingest_data(force_reload=False)

    def recommend(self, preferences: UserPreferences) -> RecommendationResponse:
        """
        Coordinates the entire recommendation pipeline:
        Filter -> Ingest candidates -> Prompt -> LLM complete -> Parser -> Format response
        """
        self.load_dataset()
        
        is_external = (
            preferences.state.lower() != "karnataka" or 
            preferences.city.lower() != "bangalore"
        )
        
        candidates = []
        
        if not is_external:
            # Filter candidates using FilterEngine
            # Handle "All" cuisine selection
            cuisine_val = None if preferences.cuisine == "All" or not preferences.cuisine.strip() else preferences.cuisine
            
            candidates_df = self.filter_engine.apply_filters(
                self.df,
                location=preferences.location,
                budget=preferences.budget,
                cuisine=cuisine_val,
                min_rating=preferences.min_rating,
                limit=30  # Cap candidates before LLM
            )
            
            if candidates_df.empty:
                return RecommendationResponse(
                    summary="No restaurants match your selection criteria.", 
                    recommendations=[]
                )

            # Convert DataFrame candidates to Restaurant Pydantic models
            for idx, row in candidates_df.iterrows():
                # Generate deterministic unique ID from name + location for grounding
                r_id = hashlib.md5(f"{row['name']}_{row['location']}".encode()).hexdigest()[:8]
                
                cuisines_list = [c.strip() for c in row['cuisines'].split(',') if c.strip()]
                
                # Map cost to budget band dynamically using filter thresholds
                cost = row['approx_cost']
                low_bound = self.filter_engine.budget_bounds['low']
                med_upper = self.filter_engine.budget_bounds['medium_upper']
                
                if cost <= low_bound:
                    budget_band = "low"
                elif cost > med_upper:
                    budget_band = "high"
                else:
                    budget_band = "medium"

                candidates.append(Restaurant(
                    id=r_id,
                    name=row['name'],
                    location=row['location'],
                    cuisines=cuisines_list,
                    rating=row['rating'],
                    estimated_cost=cost,
                    budget_band=budget_band
                ))

        # Build prompt & system instruction
        system_instruction = prompt_builder.get_system_instruction(is_external=is_external)
        prompt = prompt_builder.build_prompt(preferences, candidates)

        # Complete and Parse
        try:
            raw_text = self.llm_client.complete(system_instruction, prompt)
            response = response_parser.parse_response(raw_text, candidates)
        except Exception as e:
            print(f"Orchestrator: Call to LLMClient failed. Invoking parser fallback. Error: {e}")
            if is_external:
                return RecommendationResponse(
                    summary="Failed to get external recommendations from AI.",
                    recommendations=[]
                )
            response = response_parser.generate_fallback_response(candidates, top_k=preferences.top_k)

        # Ensure recommendation list size matches user requested top_k
        response.recommendations = response.recommendations[:preferences.top_k]
        return response
