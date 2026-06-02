# 🍔 Zomato AI Restaurant Recommender

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=https://github.com/niki019/zomato_milestone)

An intelligent, premium mobile-responsive restaurant suggestion dashboard combining deterministic SQL-like dataset filtering with LLM-powered personalization.

This project is built using a decoupled architecture consisting of a **FastAPI REST backend** and a **Streamlit frontend dashboard**.

---

## 🌟 Key Features

*   **State & City Selection (External Generative Search)**:
    *   **Local Database Mode**: When searching in `Karnataka` ➔ `Bangalore`, the application queries a locally cached Hugging Face Zomato dataset (12k+ restaurants, 95 neighborhoods).
    *   **Generative Mode**: When searching in other states/cities (like `Delhi` ➔ `New Delhi` or `Maharashtra` ➔ `Mumbai`), the orchestrator automatically switches to Generative Search, using the LLM's own knowledge base to recommend top-tier real venues fitting the request constraints.
*   **Dual-Layer Recommendation Engine**:
    *   **Layer 1 (Deterministic Filter)**: Cuts down options based on neighborhood, cuisine matching, rating thresholds, and budget limits.
    *   **Layer 2 (LLM Personalization & Grounding)**: Enriches prompt with remaining candidates and custom preferences (e.g. *"rooftop seating"*, *"romantic date night"*) to dynamically rank and generate tailored comparative explanations.
*   **Aesthetic Mobile UI/UX**:
    *   Dark space theme with glassmorphic cards and left gradient accents.
    *   Sticky top bar, header metric counters, and floating sliders action button (`🎛️`) that programmatically toggles the preference sidebar for native mobile experiences.

---

## 🚀 One-Click Cloud Deployment

You can deploy this dashboard directly on **Streamlit Community Cloud** in seconds using the button below:

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=https://github.com/niki019/zomato_milestone)

### Setting up Secrets
Once deployed on Streamlit Cloud, go to **Settings** ➔ **Secrets** and enter your configurations in TOML format:
```toml
LLM_PROVIDER = "groq"
GROQ_API_KEY = "your_groq_api_key"
LLM_MODEL = "llama-3.3-70b-versatile"
DATA_PATH = "backend/data/zomato_cache.csv"
BUDGET_LOW_MAX = 500
BUDGET_MEDIUM_MAX = 1500
```
*The app will automatically run in in-process fallback mode using the locally cached dataset.*

---

## ⚙️ Running Locally (Decoupled Mode)

### Prerequisites
*   Python 3.10+
*   Groq API Key (loaded from `.env`)

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/niki019/zomato_milestone.git
cd zomato_milestone
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Secrets Configuration
Create a `.env` file in the root directory:
```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama-3.3-70b-versatile
DATA_PATH=backend/data/zomato_cache.csv
BUDGET_LOW_MAX=500
BUDGET_MEDIUM_MAX=1500
```

### 3. Run FastAPI Backend
```bash
uvicorn backend.api:app --host 127.0.0.1 --port 8000
```
*API docs will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)*

### 4. Run Streamlit Frontend
```bash
streamlit run app.py --server.port 8501
```
*UI dashboard will be available at [http://localhost:8501](http://localhost:8501)*

---

## 📂 Project Architecture

Detailed system designs and guides are stored in the [docs/](file:///e:/zomato_recommender/docs/) folder:
*   [context.md](file:///e:/zomato_recommender/docs/context.md): Goals and context.
*   [architecture.md](file:///e:/zomato_recommender/docs/architecture.md): logical layers and data flow diagrams.
*   [deployment_plan.md](file:///e:/zomato_recommender/docs/deployment_plan.md): Host setup steps for both monolithic and multi-service deployment.
*   [edge-case.md](file:///e:/zomato_recommender/docs/edge-case.md): Budget-band logic and filter relaxation.
