# Deployment Plan: Zomato AI Restaurant Recommender on Streamlit Cloud

This document outlines the deployment strategy, prerequisites, configuration, and step-by-step process for deploying the Zomato AI Restaurant Recommender application onto **Streamlit Community Cloud**.

---

## 1. Deployment Architecture Options

Since the application is built in a decoupled manner (FastAPI backend + Streamlit frontend), we have two deployment configurations:

### Option A: In-Process Fallback Mode (Recommended & Simplest)
In this mode, we deploy only the Streamlit application to Streamlit Cloud. 
* **How it works**: Streamlit Cloud runs `app.py`. Since no local FastAPI backend is active on the same container, the frontend automatically falls back to in-process execution. It loads the `zomato_cache.csv` dataset, initializes the `RecommendationOrchestrator`, and directly issues API calls to Groq.
* **Pros**: Free, extremely fast to set up, requires hosting on only a single platform.
* **Cons**: No public REST API endpoint exposed for other clients.

```
┌────────────────────────────────────────────────────────┐
│               Streamlit Community Cloud                │
│                                                        │
│   ┌────────────┐       In-Process       ┌──────────┐   │
│   │   app.py   │ ─────────────────────> │ Orchest- │   │
│   │ (Frontend) │ <───────────────────── │  rator   │   │
│   └────────────┘                        └──────────┘   │
│         │                                     │        │
│         │ User inputs                         │ Ground │
│         ▼                                     ▼        │
│    [ Web Page ]                       [(zomato_cache)] │
└─────────┼──────────────────────────────────────────────┘
          │
          │ Groq API Call
          ▼
    ┌───────────┐
    │ Groq LLM  │
    └───────────┘
```

### Option B: Fully Decoupled Multi-Service Mode (Production Grade)
In this mode, the backend API and frontend are hosted on separate, specialized services.
* **FastAPI Backend**: Deployed to a free/low-cost cloud host like **Render**, **Railway**, or **Fly.io** (running `uvicorn backend.api:app`).
* **Streamlit Frontend**: Deployed to **Streamlit Community Cloud**, configured with a `BACKEND_URL` pointing to the public Render/Railway domain.
* **Pros**: Maintains complete separation of concerns; the FastAPI backend remains active and available for mobile apps, web hooks, or third-party integrations.
* **Cons**: Render free-tier web services have cold starts (spin-down after 15 mins of inactivity).

---

## 2. Option A: Step-by-Step In-Process Deployment

### Step 1: Prepare the Code Repository
Ensure your GitHub repository has the following folder structure:
```text
├── .streamlit/
│   └── config.toml          # Custom theme/configuration
├── backend/
│   ├── data/
│   │   └── zomato_cache.csv # The preprocessed cache dataset
│   ├── filter_engine.py
│   ├── ingest.py
│   ├── llm_recommender.py
│   ├── models.py
│   ├── orchestrator.py
│   ├── prompt_builder.py
│   └── response_parser.py
├── app.py                   # Main Streamlit frontend
├── requirements.txt         # Project dependencies
└── README.md
```

### Step 2: Configure Dependencies
Your `requirements.txt` must include all packages needed for in-process execution:
```text
streamlit>=1.30.0
fastapi>=0.100.0
uvicorn>=0.22.0
pandas>=2.0.0
requests>=2.31.0
groq>=0.4.0
pydantic>=2.0.0
```

### Step 3: Set Up Streamlit Secrets
Do **NOT** commit your `.env` file to Github. Instead, store secrets securely on Streamlit Cloud:
1. Log in to [share.streamlit.io](https://share.streamlit.io/).
2. Select your deployed app and click **Settings** ➔ **Secrets**.
3. Add your Groq API key in TOML format:
   ```toml
   LLM_PROVIDER = "groq"
   GROQ_API_KEY = "gsk_ANdnhkMnsWIVLmy92SBo... (Your actual API key)"
   LLM_MODEL = "llama-3.3-70b-versatile"
   DATA_PATH = "backend/data/zomato_cache.csv"
   BUDGET_LOW_MAX = 500
   BUDGET_MEDIUM_MAX = 1500
   ```
4. Streamlit will automatically map these TOML keys to `os.environ` at runtime, which our configuration loaders will consume.

### Step 4: Launch the App
1. On the Streamlit Cloud dashboard, click **New app**.
2. Select your Repository, Branch, and set the Main file path to `app.py`.
3. Click **Deploy!**

---

## 3. Option B: Step-by-Step Decoupled Deployment

### Step 1: Deploy FastAPI Backend (e.g., Render)
1. Sign up on [Render.com](https://render.com).
2. Click **New** ➔ **Web Service** and link your GitHub repository.
3. Configure the build parameters:
   * **Runtime**: `Python`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `python -m uvicorn backend.api:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables under **Environment**:
   * `GROQ_API_KEY` = `(your_groq_key)`
   * `LLM_PROVIDER` = `groq`
   * `DATA_PATH` = `backend/data/zomato_cache.csv`
5. Note the generated service URL (e.g., `https://zomato-ai-backend.onrender.com`).

### Step 2: Deploy Streamlit Frontend (Streamlit Cloud)
1. Deploy `app.py` on Streamlit Cloud as described in Option A.
2. In the Streamlit Cloud **Secrets** editor, add the backend connection URL:
   ```toml
   BACKEND_URL = "https://zomato-ai-backend.onrender.com"
   GROQ_API_KEY = "(fallback_groq_key)"
   ```
3. Update [app.py](file:///e:/zomato_recommender/app.py) to read `BACKEND_URL` dynamically from the environment if present:
   ```python
   import os
   backend_url = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
   health_resp = requests.get(f"{backend_url}/api/v1/health", timeout=2)
   ```

---

## 4. Verification and Troubleshooting

* **Health Check Fails**: If the connection indicator shows `Disconnection (Running In-Process)`, verify that your backend URL is active and accessible via HTTPS.
* **Large File Cache Limit**: Streamlit Cloud has a default memory limit of **1 GB**. The `zomato_cache.csv` dataset is small (~12,000 records, ~10MB) and loads in under 1 second, easily fitting within limits.
* **Secrets Loading**: If the app fails with "Groq API Key not found", verify that you have entered `GROQ_API_KEY` in the TOML Secrets tab on the dashboard without typos.
