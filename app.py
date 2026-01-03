import os
import streamlit as st
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt

# --- IMPORT NEW COMPONENTS ---
from components.event_overview import render_event_overview
from components.strategy_view import render_strategy_view
from components.telemetry_view import render_telemetry_view
from components.motec_view import render_motec_view
from components.ai_predictor import render_ai_predictor

# 1. SETUP
st.set_page_config(page_title="Apex Intelligence", layout="wide")
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme='fastf1')

cache_dir = 'cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

fastf1.Cache.enable_cache(cache_dir)


# 2. LOAD DATA
@st.cache_data
def load_session_data(year, gp, session_type):
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    return session


# 3. SIDEBAR
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/1200px-F1.svg.png", width=100)
st.sidebar.title("F1 Telemetry & AI")

year = st.sidebar.selectbox("Year", [2025, 2024], index=0)
schedule = fastf1.get_event_schedule(year, include_testing=False)
gp = st.sidebar.selectbox("Grand Prix", schedule['EventName'].tolist(), index=0)
session_type = st.sidebar.selectbox("Session", ["FP1", "FP2", "FP3", "Q", "R"], index=4)

if st.sidebar.button("Load Session Data", type="primary"):
    with st.spinner(f"Loading {year} {gp} {session_type}..."):
        try:
            st.session_state['session'] = load_session_data(year, gp, session_type)
            st.success("Data Loaded!")
        except Exception as e:
            st.error(f"Error: {e}")

# 4. MAIN APP
if 'session' in st.session_state:
    session = st.session_state['session']

    # Define Tabs
    tabs = st.tabs(["🏁 Event Overview", "📈 Telemetry", "🧠 AI Predictor", "🏎️ Strategy", "🎮 Sim Export"])

    with tabs[0]:
        render_event_overview(session)

    with tabs[1]:
        render_telemetry_view(session)

    with tabs[2]: # The AI Predictor Tab
        render_ai_predictor(session)

    with tabs[3]: # The Strategy Tab
        render_strategy_view(session)

    with tabs[4]:
        render_motec_view(session)

else:
    st.info("👈 Select a race and click **Load Session Data** to start.")