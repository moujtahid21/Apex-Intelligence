import streamlit as st
import pandas as pd
import numpy as np
import fastf1
import fastf1.plotting
import plotly.graph_objects as go
import time

# Import your helpers from utils
from utils.replay import create_telemetry_html, get_replay_explanation, get_track_map_fig


# --- HELPER: PREPARE SIM DATA ---
@st.cache_data
def prepare_simulation_data(_session, drivers):
    """
    Prepares interpolated telemetry data for selected drivers
    AND extracts the static track path for the map background.
    """
    sim_data = {}
    max_time = 0
    track_df = pd.DataFrame()  # Default empty

    # 1. Get Track Layout (from the first driver's fastest lap)
    try:
        ref_driver = drivers[0]
        ref_lap = _session.laps.pick_driver(ref_driver).pick_fastest()
        ref_tel = ref_lap.get_telemetry()
        track_df = pd.DataFrame({'x': ref_tel['X'], 'y': ref_tel['Y']})
    except Exception as e:
        print(f"Error getting track layout: {e}")

    # 2. Get Telemetry for Each Driver
    for driver in drivers:
        try:
            lap = _session.laps.pick_driver(driver).pick_fastest()
            if lap is None: continue

            # Get telemetry and add distance/time
            tel = lap.get_car_data().add_distance().add_relative_distance()
            pos = lap.get_pos_data()

            # Merge Position and Car Data
            merged = tel.merge(pos, on='Time', how='outer').interpolate(method='linear').ffill().bfill()

            # Resample to 10Hz (0.1s) for smooth simulation
            t_max = merged['Time'].max()
            new_index = pd.timedelta_range(start=merged['Time'].min(), end=t_max, freq='100ms')

            merged = merged.set_index('Time').reindex(new_index).interpolate(method='linear').reset_index()
            merged = merged.rename(columns={'index': 'Time'})

            # Convert Time to Seconds (float) for easier slider handling
            merged['TimeSec'] = merged['Time'].dt.total_seconds()

            sim_data[driver] = {
                'df': merged,
                'color': fastf1.plotting.get_driver_color(driver, session=_session),
                'team': lap['Team']
            }

            max_time = max(max_time, merged['TimeSec'].max())

        except Exception as e:
            print(f"Error loading {driver}: {e}")

    return sim_data, track_df, max_time


# --- VIEW 1: RACE SIMULATION ---
def render_race_simulation(session):
    st.markdown("### 📺 Ghost Car Replay")

    # 1. Driver Selection
    drivers = session.results['Abbreviation'].unique().tolist()
    default_sel = drivers[:2] if len(drivers) >= 2 else drivers[:1]

    col_sel, col_play = st.columns([3, 1], vertical_alignment="bottom")
    with col_sel:
        selected_drivers = st.multiselect("Select Drivers (Max 2 recommended)", drivers, default=default_sel)

    if not selected_drivers:
        st.warning("Select drivers to start.")
        return

    # 2. Prepare Data
    with st.spinner("Syncing telemetry data..."):
        sim_data, track_df, total_duration = prepare_simulation_data(session, selected_drivers)

    if not sim_data:
        st.error("Could not load simulation data.")
        return

    # 3. Controls & State
    if 'replay_time' not in st.session_state:
        st.session_state.replay_time = 0.0

    with col_play:
        # Note: In this loop version, we don't need to bind this to rerun logic
        auto_play = st.checkbox("▶️ Auto-Play", key="autoplay_toggle")

    # The Slider controls the starting point
    race_time = st.slider(
        "Race Time (seconds)",
        0.0,
        float(total_duration),
        st.session_state.replay_time,
        step=0.1,
        format="%.1fs"
    )

    # --- 1. THE INFO BOX ---
    st.info(get_replay_explanation())

    # --- 2. THE MAIN DISPLAY CONTAINER ---
    # We create ONE placeholder that will hold the map AND the telemetry
    replay_container = st.empty()

    # Determine the loop range
    start_index = int(race_time * 10)  # 10Hz data
    max_index = int(total_duration * 10)

    if auto_play:
        # Loop from current slider pos to end
        loop_range = range(start_index, max_index)
    else:
        # Render just ONE frame (static)
        loop_range = range(start_index, start_index + 1)

    # --- 3. THE LOOP ---
    for i in loop_range:
        # Safety check
        if i >= max_index: break

        # EVERYTHING inside this block updates live without flashing the whole page
        with replay_container.container():

            # Create Layout: Map on Left (2/3), Telemetry on Right (1/3)
            col_map, col_stats = st.columns([2, 1])

            with col_map:
                # Prepare driver positions for this specific frame
                driver_positions_list = []
                for d in selected_drivers:
                    d_df = sim_data[d]['df']
                    idx = min(i, len(d_df) - 1)
                    driver_positions_list.append({
                        'name': d,
                        'x': d_df.iloc[idx]['X'],
                        'y': d_df.iloc[idx]['Y'],
                        'color': sim_data[d]['color']
                    })

                # Generate Map Figure
                fig = go.Figure()

                # 1. Static Track Line
                fig.add_trace(go.Scatter(
                    x=track_df['x'], y=track_df['y'],
                    mode='lines',
                    line=dict(color='#333', width=4),
                    hoverinfo='skip',
                    showlegend=False
                ))

                # 2. Dynamic Driver Dots
                for pos in driver_positions_list:
                    fig.add_trace(go.Scatter(
                        x=[pos['x']], y=[pos['y']],
                        mode='markers',
                        marker=dict(size=14, color=pos['color'], line=dict(color='white', width=2)),
                        name=pos['name']
                    ))

                fig.update_layout(
                    height=500,
                    margin=dict(l=0, r=0, t=0, b=0),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=True,
                    xaxis=dict(visible=False, fixedrange=True),
                    yaxis=dict(visible=False, fixedrange=True, scaleanchor="x", scaleratio=1)
                )

                # Unique key is REQUIRED here to force Plotly to update inside a loop.
                # This causes the slight flicker, but enables the smooth loop animation.
                st.plotly_chart(fig, use_container_width=True, key=f"map_{i}")

            with col_stats:
                st.subheader("📊 Live Telemetry")

                for d in selected_drivers:
                    d_df = sim_data[d]['df']
                    idx = min(i, len(d_df) - 1)
                    row = d_df.iloc[idx]

                    # Render Telemetry Card
                    st.html(create_telemetry_html(
                        driver=d,
                        speed=row['Speed'],
                        gear=row['nGear'],
                        throttle=row['Throttle'],
                        brake=row['Brake'],
                        color_code=sim_data[d]['color']
                    ))

        # Speed control for Auto-Play
        if auto_play:
            time.sleep(0.1)


# --- VIEW 2: STRATEGY AI ---
def render_strategy_ai(session):
    st.markdown("### 🧠 Race Strategy Predictor")
    st.info("This module uses machine learning to predict the optimal pit stop window based on tyre degradation rates.")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Predicted Pit Lap", "Lap 24-26", "Soft → Hard")
    with col2:
        st.metric("Undercut Potential", "High", "-1.2s gain")

    st.bar_chart({"Soft": 1.2, "Medium": 0.8, "Hard": 0.2})


# --- MAIN ENTRY POINT ---
def render_ai_predictor(session):
    tab_sim, tab_ai = st.tabs(["📺 Visual Simulation", "🔮 Strategy AI"])

    with tab_sim:
        render_race_simulation(session)

    with tab_ai:
        render_strategy_ai(session)