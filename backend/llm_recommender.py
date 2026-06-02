import os
import json
from dotenv import load_dotenv

# Load env variables from the root .env file if it exists
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

class LLMClient:
    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER", "groq").lower()
        self.groq_key = os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        self.groq_model = os.getenv("LLM_MODEL") or os.getenv("GROQ_MODEL", "llama-3.3-70b-specdec")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))

        self.client_type = None

        # Check Groq first
        if (self.llm_provider == "groq" or not self.gemini_key) and self.groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_key)
                self.client_type = "groq"
                print("LLMClient: Initialized with Groq SDK.")
            except ImportError:
                print("Warning: Groq SDK not found.")

        # Check Gemini fallback
        if not self.client_type and self.gemini_key:
            try:
                from google import genai
                self.genai_client = genai.Client(api_key=self.gemini_key)
                self.client_type = "gemini_new"
                print("LLMClient: Initialized with Google GenAI SDK.")
            except ImportError:
                try:
                    import google.generativeai as legacy_genai
                    legacy_genai.configure(api_key=self.gemini_key)
                    self.genai_model_client = legacy_genai.GenerativeModel(self.gemini_model)
                    self.client_type = "gemini_legacy"
                    print("LLMClient: Initialized with legacy Google GenerativeAI SDK.")
                except ImportError:
                    print("Warning: Gemini SDKs not found.")
        
        # Check OpenAI fallback
        if not self.client_type and self.openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_key)
                self.client_type = "openai"
                print("LLMClient: Initialized with OpenAI SDK.")
            except ImportError:
                print("Warning: OpenAI SDK not found.")

        if not self.client_type:
            self.client_type = "mock"
            print("LLMClient: No API keys found or libraries missing. Running in MOCK Mode.")

    def complete(self, system_instruction: str, prompt: str) -> str:
        """
        Executes completion logic using the configured client type.
        Returns the raw string output from the LLM model.
        """
        if self.client_type == "mock":
            # In mock mode, we raise exception to trigger ResponseParser fallback, 
            # or return a clean JSON string matching output schema.
            return self._generate_mock_completion(prompt)

        try:
            if self.client_type == "groq":
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.llm_temperature,
                    response_format={"type": "json_object"}
                )
                return response.choices[0].message.content

            elif self.client_type == "gemini_new":
                from google.genai import types
                response = self.genai_client.models.generate_content(
                    model=self.gemini_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        temperature=self.llm_temperature
                    )
                )
                return response.text

            elif self.client_type == "gemini_legacy":
                response = self.genai_model_client.generate_content(
                    prompt,
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": self.llm_temperature
                    }
                )
                return response.text

            elif self.client_type == "openai":
                response = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.llm_temperature,
                    response_format={"type": "json_object"}
                )
                return response.choices[0].message.content

        except Exception as e:
            print(f"LLMClient complete call failed: {e}. Raising exception for fallback.")
            raise e

    def _generate_mock_completion(self, prompt: str) -> str:
        """Helper to output static mockup JSON for testing purposes."""
        # Simple extraction of candidate list from prompt to simulate LLM ranking
        try:
            # Look for JSON block in prompt representing candidate restaurants
            recs = []
            candidates_start = prompt.find("Candidate Restaurants:")
            task_start = prompt.find("Task Instructions:")
            if candidates_start != -1 and task_start != -1:
                json_str = prompt[candidates_start + len("Candidate Restaurants:"):task_start].strip()
                candidates_list = json.loads(json_str)
                
                for idx, c in enumerate(candidates_list[:5]):
                    recs.append({
                        "restaurant_id": c["id"],
                        "rank": idx + 1,
                        "explanation": (
                            f"Mock LLM: {c['name']} is highly rated at {c['rating']}/5. "
                            f"It is located in {c['location']} and serves {c['cuisines']}. "
                            f"Estimating around ₹{c['approx_cost']} for two, matching your target budget."
                        )
                    })
            
            mock_res = {
                "summary": "Mock LLM Recommendations selected based on dataset parameters.",
                "recommendations": recs
            }
            return json.dumps(mock_res)
        except Exception:
            # Basic fallback JSON
            return json.dumps({
                "summary": "Mock LLM: fallback response generated.",
                "recommendations": []
            })
