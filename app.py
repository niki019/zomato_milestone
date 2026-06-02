import os
import streamlit as st
import pandas as pd
import requests
from backend.models import UserPreferences
from backend.orchestrator import RecommendationOrchestrator

# Set page config
st.set_page_config(
    page_title="Zomato AI Recommend",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Custom CSS for Premium Design & Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    /* Global Typography & Font override */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Style the main container */
    .stApp {
        background: linear-gradient(135deg, #0f0c1b 0%, #15102a 50%, #06020f 100%);
        color: #f1ecff;
    }

    /* Hide Streamlit header & default hamburger menu */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    #MainMenu {
        visibility: hidden;
    }
    
    /* Page padding override for native app feel */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 5rem !important;
    }

    /* Custom Nav Bar */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(16, 11, 37, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    .nav-title {
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #ffffff 0%, #dfd7f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 10px rgba(255, 255, 255, 0.1);
    }
    .nav-icon {
        color: #dfd7f7;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .nav-icon:hover {
        color: #ff4e50;
        transform: scale(1.1);
    }

    /* Subtitle centering and style */
    .app-subtitle {
        font-size: 1rem;
        font-weight: 300;
        color: #b2a8d3;
        margin-bottom: 2rem;
        text-align: center;
        line-height: 1.5;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Sidebar custom styling */
    section[data-testid="stSidebar"] {
        background-color: #100b25 !important;
        border-right: 1px solid rgba(255, 78, 80, 0.15);
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1, 
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #ff4e50;
    }

    /* Input elements style customization */
    .stButton>button {
        background: linear-gradient(90deg, #ff4e50 0%, #f9d423 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255, 78, 80, 0.4) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 78, 80, 0.6) !important;
    }

    /* Metric cards styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.25rem 0.5rem;
        text-align: center;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .metric-card:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 78, 80, 0.2);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.03em;
        margin-bottom: 0.2rem;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #8b7fa9;
        font-weight: 400;
    }

    /* Cards container & styling */
    .restaurant-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        backdrop-filter: blur(12px);
        position: relative;
        overflow: hidden;
    }
    
    .restaurant-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(to bottom, #ff4e50, #f9d423);
    }
    
    .restaurant-card:hover {
        transform: translateY(-4px);
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 78, 80, 0.3);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .restaurant-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    .restaurant-rating {
        background: linear-gradient(45deg, #11998e, #38ef7d);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .restaurant-meta {
        font-size: 0.9rem;
        color: #b2a8d3;
        margin-bottom: 1rem;
    }
    
    .restaurant-meta span {
        margin-right: 1.5rem;
    }

    .ai-badge {
        display: inline-block;
        background: rgba(255, 78, 80, 0.1);
        border: 1px solid rgba(255, 78, 80, 0.3);
        color: #ff4e50;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

    .ai-explanation {
        background: rgba(255, 78, 80, 0.04);
        border-left: 3px solid #ff4e50;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        color: #ebdffc;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .summary-box {
        background: rgba(255, 78, 80, 0.03);
        border: 1px dashed rgba(255, 78, 80, 0.4);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2.5rem;
        font-size: 1.05rem;
        color: #ebdffc;
        line-height: 1.6;
        box-shadow: 0 0 25px rgba(255, 78, 80, 0.08);
        display: flex;
        align-items: flex-start;
        gap: 1.2rem;
    }
    .summary-icon {
        font-size: 1.6rem;
        color: #ff4e50;
        margin-top: -0.1rem;
        filter: drop-shadow(0 0 8px rgba(255, 78, 80, 0.6));
    }
    .summary-text {
        flex: 1;
    }
    .summary-title {
        font-weight: 700;
        color: #ff4e50;
        margin-right: 0.4rem;
    }

    /* Floating Action Button (FAB) */
    .fab-button {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 3.5rem;
        height: 3.5rem;
        background: linear-gradient(135deg, #ff4e50 0%, #f9d423 100%);
        color: #ffffff;
        border-radius: 16px;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: 0 8px 25px rgba(255, 78, 80, 0.4);
        cursor: pointer;
        z-index: 999999;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .fab-button:hover {
        transform: scale(1.1) rotate(90deg);
        box-shadow: 0 12px 30px rgba(255, 78, 80, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# 1. Initialize Orchestrator (it handles cache and filtering internally)
orchestrator = RecommendationOrchestrator()
orchestrator.load_dataset()
df = orchestrator.df

# Start API backend in background if running locally or on single cloud instance
import socket
import subprocess
import sys
import time
import os

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000").rstrip('/')
backend_healthy = False

if "127.0.0.1" in BACKEND_URL or "localhost" in BACKEND_URL:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(("127.0.0.1", 8000))
        s.close()
        backend_healthy = True
    except Exception:
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
            subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "backend.api:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "warning"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env
            )
            time.sleep(4.0)  # Allow API startup & dataset loading on cloud VM
        except Exception:
            pass

# Verify health status if not already set to True by connection check
if not backend_healthy:
    try:
        import requests
        health_resp = requests.get(f"{BACKEND_URL}/api/v1/health", timeout=2)
        if health_resp.status_code == 200:
            backend_healthy = True
    except Exception:
        pass

# Top Navigation Bar (Clean logo navbar without sidebar toggle)
st.markdown("""
<div class="nav-bar">
    <div style="font-size: 1.5rem; font-weight: 700; letter-spacing: -0.02em; background: linear-gradient(90deg, #ffffff 0%, #dfd7f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🍔 Zomato AI Recommender
    </div>
    <div class="nav-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1.5rem; height: 1.5rem;">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
        </svg>
    </div>
</div>
""", unsafe_allow_html=True)

# Subtitle centered below navbar
st.markdown("<div class='app-subtitle'>An intelligent restaurant suggestion service combining structured datasets with LLM-powered personalization.</div>", unsafe_allow_html=True)

# Centered Status Badge
if backend_healthy:
    st.markdown("<div style='text-align: center; margin-top: -1rem; margin-bottom: 1.5rem;'><span style='background: rgba(17, 153, 142, 0.15); border: 1px solid #11998e; color: #38ef7d; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;'>🟢 API Backend: Connected</span></div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='text-align: center; margin-top: -1rem; margin-bottom: 1.5rem;'><span style='background: rgba(255, 78, 80, 0.15); border: 1px solid #ff4e50; color: #ff8c94; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;'>🟢 System Status: Active (In-Process Fallback)</span></div>", unsafe_allow_html=True)

# Dynamic metrics row
val_restaurants = "12k"
val_neighborhoods = "95"
val_rating = "4.2"

if df is not None:
    try:
        total_cnt = len(df)
        if total_cnt >= 1000:
            val_restaurants = f"{total_cnt // 1000}k"
        else:
            val_restaurants = str(total_cnt)
        
        val_neighborhoods = str(df['location'].dropna().nunique())
        avg_r = df[df['rating'] > 0]['rating'].mean()
        val_rating = f"{avg_r:.1f}"
    except Exception:
        pass

metric_cols = st.columns(3)
with metric_cols[0]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{val_restaurants}</div>
        <div class="metric-label">Restaurants</div>
    </div>
    """, unsafe_allow_html=True)
with metric_cols[1]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{val_neighborhoods}</div>
        <div class="metric-label">Neighborhoods</div>
    </div>
    """, unsafe_allow_html=True)
with metric_cols[2]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{val_rating}</div>
        <div class="metric-label">Avg Rating</div>
    </div>
    """, unsafe_allow_html=True)

# 2. Main Page Preferences Control Panel (instead of sidebar)
if "search_performed" not in st.session_state:
    st.session_state.search_performed = False
if "last_query" not in st.session_state:
    st.session_state.last_query = {}
if "last_results" not in st.session_state:
    st.session_state.last_results = None

# We use st.container with border for a beautiful, persistent search panel card
with st.container(border=True):
    st.markdown("<h3 style='margin-top: 0;'>🔍 Search Preferences & Filters</h3>", unsafe_allow_html=True)
    
    col_state, col_city, col_loc = st.columns(3)
    with col_state:
        state_input = st.selectbox("State", options=["Karnataka", "Delhi", "Maharashtra"], index=0)
    with col_city:
        if state_input == "Karnataka":
            cities = ["Bangalore"]
        elif state_input == "Delhi":
            cities = ["New Delhi"]
        elif state_input == "Maharashtra":
            cities = ["Mumbai"]
        else:
            cities = []
        city_input = st.selectbox("City", options=cities, index=0)
    with col_loc:
        is_local_db = (state_input == "Karnataka" and city_input == "Bangalore")
        if is_local_db and df is not None:
            locations = sorted(df['location'].dropna().unique().tolist())
            location_input = st.selectbox(
                "Location / Neighborhood", 
                options=locations, 
                index=locations.index("Banashankari") if "Banashankari" in locations else 0
            )
        else:
            default_loc = "Connaught Place" if city_input == "New Delhi" else "Bandra"
            location_input = st.text_input("Location / Neighborhood", default_loc)
        
    col_cui, col_bud, col_rat = st.columns(3)
    with col_cui:
        if is_local_db and df is not None:
            all_cuisines = set()
            for c_str in df['cuisines'].dropna().unique():
                for cuisine in c_str.split(','):
                    all_cuisines.add(cuisine.strip())
            common_cuisines = sorted(list(all_cuisines))
            cuisine_input = st.selectbox("Cuisine Choice", options=["All"] + common_cuisines, index=0)
        else:
            cuisine_input = st.text_input("Cuisine Choice", "All")
    with col_bud:
        budget_input = st.selectbox("Budget Level", ["Low", "Medium", "High"], index=1)
    with col_rat:
        min_rating = st.slider("Minimum Rating", 0.0, 5.0, 3.5, 0.1)
        
    additional_pref = st.text_input(
        "Specific Preferences (Optional)", 
        placeholder="e.g. rooftop seating, quiet romantic vibe, famous for desserts"
    )
    
    search_clicked = st.button("Find Recommendations", type="primary", use_container_width=True)

# Build current query dictionary to check if inputs changed
current_query = {
    "state": state_input,
    "city": city_input,
    "location": location_input,
    "budget": budget_input.lower(),
    "cuisine": cuisine_input,
    "min_rating": min_rating,
    "additional_preferences": additional_pref.strip() if additional_pref.strip() else None
}

# 3. Execution & Rerun logic
if search_clicked:
    st.session_state.search_performed = True
    st.session_state.last_query = current_query
    
    # Prepare inputs as Pydantic model
    prefs = UserPreferences(
        state=state_input,
        city=city_input,
        location=location_input,
        budget=budget_input.lower(),
        cuisine=cuisine_input,
        min_rating=min_rating,
        additional_preferences=additional_pref if additional_pref.strip() else None,
        top_k=5
    )
    
    with st.spinner("AI is generating recommendations and ranking..."):
        response = None
        # Attempt to call decoupled FastAPI backend first
        if backend_healthy:
            try:
                payload = prefs.dict()
                response_api = requests.post(
                    f"{BACKEND_URL}/api/v1/recommendations", 
                    json=payload, 
                    timeout=60
                )
                if response_api.status_code == 200:
                    from backend.models import RecommendationResponse
                    response = RecommendationResponse(**response_api.json())
                else:
                    st.warning(f"Backend API returned status {response_api.status_code}. Fallback triggered.")
            except Exception as e:
                st.warning(f"Error calling Backend API: {e}. Fallback triggered.")
        
        # Fallback to local execution if backend call failed or was disconnected
        if response is None:
            if df is None:
                st.error("No dataset available to query for local recommendation.")
            else:
                response = orchestrator.recommend(prefs)
        
        st.session_state.last_results = response

# 4. Display Results or Landing State
if st.session_state.search_performed and st.session_state.last_results is not None:
    # Check if filters have changed relative to the query that produced the currently visible results
    filters_changed = False
    for k, v in current_query.items():
        if st.session_state.last_query.get(k) != v:
            filters_changed = True
            break
            
    if filters_changed:
        st.info("💡 **Filters changed!** Click **Find Recommendations** to refresh the recommendations with your new preferences.")
        
    response = st.session_state.last_results
    
    # Render Summary
    if response.summary:
        st.markdown(f"""
        <div class="summary-box">
            <span class="summary-icon">💡</span>
            <div class="summary-text">
                <span class="summary-title">AI Summary:</span> {response.summary}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Render Recommendations
    if not response.recommendations:
        st.warning("No recommendations could be generated matching your filters.")
    else:
        st.subheader(f"Recommendations for you in {st.session_state.last_query.get('location', '')}")
        for item in response.recommendations:
            rest = item.restaurant
            
            # Format card HTML
            st.markdown(f"""
            <div class="restaurant-card">
                <div class="card-header">
                    <span class="restaurant-name">{rest.name}</span>
                    <span class="restaurant-rating">★ {rest.rating}</span>
                </div>
                <div class="restaurant-meta">
                    <span>📍 <b>{rest.location}</b></span>
                    <span>🍽️ <b>{', '.join(rest.cuisines)}</b></span>
                    <span>💰 <b>₹{rest.estimated_cost} for two</b></span>
                </div>
                <div class="ai-badge">AI Insight</div>
                <div class="ai-explanation">
                    {item.explanation}
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    # Landing state info
    st.info("✨ Adjust the preferences above and click **Find Recommendations** to see your personalized restaurant picks!")
    
    # Show stats of loaded database to look professional
    if df is not None:
        st.markdown("### Database Overview")
        st.write("#### Sample Restaurants in Database")
        st.dataframe(df[['name', 'location', 'cuisines', 'rating', 'approx_cost']].head(10), use_container_width=True)
