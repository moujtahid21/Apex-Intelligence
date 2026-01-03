import streamlit as st
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import os

# --- IMPORT COMPONENTS ---
try:
    from components.event_overview import render_event_overview
    from components.telemetry_view import render_telemetry_view
    from components.motec_view import render_motec_view
    from components.strategy_view import render_strategy_view
except ImportError as e:
    st.error(f"❌ Component Import Error: {e}")

# 1. SETUP
st.set_page_config(page_title="Apex Intelligence", layout="wide")
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme='fastf1')

if not os.path.exists('cache'):
    os.makedirs('cache')
fastf1.Cache.enable_cache('cache')

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
try:
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    gp_list = schedule['EventName'].tolist()
except Exception:
    st.sidebar.warning("Could not load schedule.")
    gp_list = []

gp = st.sidebar.selectbox("Grand Prix", gp_list, index=0)
session_type = st.sidebar.selectbox("Session", ["FP1", "FP2", "FP3", "Q", "R"], index=4)

if st.sidebar.button("Load Session Data", type="primary"):
    with st.spinner(f"Loading {year} {gp} {session_type}..."):
        try:
            st.session_state['session'] = load_session_data(year, gp, session_type)
            st.success("Data Loaded!")
        except Exception as e:
            st.error(f"Error loading data: {e}")

# 4. MAIN APP LOGIC
if 'session' in st.session_state:
    session = st.session_state['session']

    # --- NAVIGATION ---
    st.markdown("""
        <style>
            div.stRadio > div[role="radiogroup"] {
                display: flex;
                justify-content: center;
                gap: 20px;
                padding-bottom: 20px;
                border-bottom: 1px solid #333; /* This is the first line */
                margin-bottom: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    views = [
        "🏁 Event Overview",
        "📈 Telemetry",
        "🧠 AI Predictor",
        "🏎️ Strategy",
        "🎮 Sim Export"
    ]

    selected_view_name = st.radio(
        "Navigation",
        views,
        horizontal=True,
        label_visibility="collapsed",
        key="current_view_selection"
    )

    # --- RENDER SELECTED VIEW ---

    try:
        if selected_view_name == "🏁 Event Overview":
            render_event_overview(session)

        elif selected_view_name == "📈 Telemetry":
            render_telemetry_view(session)

        elif selected_view_name == "🧠 AI Predictor":
            try:
                from components.ai_predictor import render_ai_predictor
                render_ai_predictor(session)
            except ImportError:
                st.warning("⚠️ AI Predictor component is missing.")
            except Exception as e:
                st.error(f"AI Model Error: {e}")

        elif selected_view_name == "🏎️ Strategy":
            render_strategy_view(session)

        elif selected_view_name == "🎮 Sim Export":
            render_motec_view(session)

    except Exception as e:
        st.error(f"❌ An error occurred in **{selected_view_name}**:")
        st.code(str(e))
        st.info("Try selecting a different driver or reloading the session data.")

else:
    st.info("👈 Select a race and click **Load Session Data** to start.")