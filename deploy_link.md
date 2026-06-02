# 🚀 Zomato AI Restaurant Recommender - Deploy & Test

Click the link below to deploy and test the app on Streamlit Cloud instantly:

👉 **[Deploy and Test Frontend Live on Streamlit Cloud](https://share.streamlit.io/deploy?repository=https://github.com/niki019/zomato_milestone&branch=main&main_file=app.py)**

---

### How to Test it:
1. Click the link above.
2. Sign in to Streamlit Cloud with your GitHub account (free).
3. Click **Deploy**.
4. Once the app starts in your browser, go to **Settings** (bottom right) ➔ **Secrets** tab, and enter your Groq API credentials:
   ```toml
   LLM_PROVIDER = "groq"
   GROQ_API_KEY = "gsk_ANdnhkMnsWIVLmy92SBo... (Your actual API key)"
   LLM_MODEL = "llama-3.3-70b-versatile"
   DATA_PATH = "backend/data/zomato_cache.csv"
   BUDGET_LOW_MAX = 500
   BUDGET_MEDIUM_MAX = 1500
   ```
5. Click **Save** and start searching!
