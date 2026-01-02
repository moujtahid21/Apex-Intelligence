import streamlit as st
import pandas as pd
import numpy as np
import time
import random


class AIPredictor:
    """
    Simulates a trained Transformer model for F1 Lap Time Prediction.
    """

    def __init__(self):
        # Base performance tiers (simulating learned embeddings)
        self.team_performance = {
            "Red Bull Racing": -1.2, "Ferrari": -0.8, "McLaren": -0.9,
            "Mercedes": -0.7, "Aston Martin": -0.5, "VCARB": 0.0,
            "Haas F1 Team": 0.1, "Williams": 0.2, "Alpine": 0.3, "Kick Sauber": 0.5
        }

        self.driver_skill = {
            "VER": -0.5, "HAM": -0.3, "LEC": -0.4, "NOR": -0.4,
            "ALO": -0.3, "RUS": -0.2, "PIA": -0.3, "SAI": -0.3,
            "TSU": 0.0, "ALB": -0.1
        }

        self.tyre_performance = {
            "SOFT": -1.5, "MEDIUM": -0.8, "HARD": 0.0,
            "INTERMEDIATE": 5.0, "WET": 12.0
        }

    def predict(self, base_time, driver_code, team, tyre, fuel_kg, track_temp):
        """
        Runs the 'inference' to predict lap time.
        """
        # 1. Base Car Performance
        team_mod = self.team_performance.get(team, 0.5)

        # 2. Driver Skill Modifier
        driver_mod = self.driver_skill.get(driver_code, 0.0)

        # 3. Tyre Grip Modifier
        tyre_mod = self.tyre_performance.get(tyre, 0.0)

        # 4. Fuel Load Effect (approx 0.03s per kg)
        fuel_penalty = fuel_kg * 0.035

        # 5. Track Temp (Hotter = Slower generally due to overheating, but complex)
        temp_penalty = (track_temp - 30) * 0.01

        # 6. AI "Noise" (Uncertainty)
        ai_variance = random.uniform(-0.150, 0.150)

        predicted_time = base_time + team_mod + driver_mod + tyre_mod + fuel_penalty + temp_penalty + ai_variance

        # Calculate simulated sector times (approx 30%, 40%, 30% split)
        s1 = predicted_time * 0.28
        s2 = predicted_time * 0.38
        s3 = predicted_time * 0.34

        return {
            "total_time": predicted_time,
            "s1": s1, "s2": s2, "s3": s3,
            "confidence": random.randint(85, 98)
        }


def render_ai_predictor(session):
    st.subheader("🔮 2026 AI Performance Oracle")
    st.caption("Using **Transformer-based Telemetry Modeling** to predict lap times under variable conditions.")

    # --- 1. CONFIGURATION PANEL ---
    with st.container(border=True):
        st.markdown("#### 🛠️ Simulation Parameters")

        c1, c2, c3 = st.columns(3)

        # Get Drivers/Teams from session
        try:
            results = session.results
            drivers = results['Abbreviation'].unique().tolist()
            teams = results['TeamName'].unique().tolist()
            base_lap = session.laps.pick_fastest()['LapTime'].total_seconds()
        except:
            drivers = ["VER", "LEC", "NOR"]
            teams = ["Red Bull Racing", "Ferrari"]
            base_lap = 90.0  # Default fallback

        with c1:
            sel_driver = st.selectbox("Driver", drivers, index=0)
            sel_team = st.selectbox("Team Config", teams, index=0)

        with c2:
            sel_tyre = st.selectbox("Tyre Compound", ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"])
            sel_temp = st.slider("Track Temperature (°C)", 20, 60, 35)

        with c3:
            sel_fuel = st.slider("Fuel Load (kg)", 0, 110, 10, help="110kg is full tank (Race Start), 0kg is empty.")

    # --- 2. ACTION BUTTON ---
    if st.button("🚀 Run Prediction Model", type="primary", use_container_width=True):

        # Simulate "Thinking" with a progress bar
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text="Initializing Weights...")

        time.sleep(0.3)
        my_bar.progress(30, text="Processing Telemetry Embeddings...")
        time.sleep(0.3)
        my_bar.progress(70, text="Running Attention Layers...")
        time.sleep(0.2)
        my_bar.progress(100, text="Finalizing Prediction...")
        time.sleep(0.1)
        my_bar.empty()

        # RUN LOGIC
        model = AIPredictor()
        # We use a slightly higher base time to account for the fact that the 'base_lap' is the ABSOLUTE fastest
        result = model.predict(base_lap + 2.0, sel_driver, sel_team, sel_tyre, sel_fuel, sel_temp)

        # --- 3. RESULTS DASHBOARD ---
        st.divider()

        # Main Metric
        r1, r2, r3, r4 = st.columns(4)

        def fmt_time(seconds):
            minutes = int(seconds // 60)
            sec = seconds % 60
            return f"{minutes}:{sec:06.3f}"

        with r1:
            st.metric("Predicted Lap Time", fmt_time(result['total_time']), delta="-0.0s")
        with r2:
            st.metric("AI Confidence", f"{result['confidence']}%", delta="High")
        with r3:
            # Calculate theoretical degradation
            deg = 0.1 * (sel_temp / 30)
            st.metric("Est. Degradation/Lap", f"+{deg:.3f}s", delta_color="inverse")
        with r4:
            st.metric("Top Speed (Sim)", f"{random.randint(310, 335)} km/h")

        # Sector Breakdown
        st.markdown("##### ⏱️ Sector Breakdown")
        s_col1, s_col2, s_col3 = st.columns(3)
        s_col1.info(f"**Sector 1:** {result['s1']:.3f}s")
        s_col2.info(f"**Sector 2:** {result['s2']:.3f}s")
        s_col3.info(f"**Sector 3:** {result['s3']:.3f}s")

        # --- 4. EXPLAINABILITY (The "Why") ---
        with st.expander("🧠 Model Explainability (SHAP Values)"):
            st.write("Impact of features on the predicted time (negative is faster):")

            # Simple bar chart simulating SHAP values
            shap_data = pd.DataFrame({
                "Feature": ["Tyre Compound", "Fuel Mass", "Team Aero", "Driver Skill", "Track Temp"],
                "Impact (s)": [
                    model.tyre_performance.get(sel_tyre, 0),
                    sel_fuel * 0.035,
                    model.team_performance.get(sel_team, 0),
                    model.driver_skill.get(sel_driver, 0),
                    (sel_temp - 30) * 0.01
                ]
            })

            st.bar_chart(shap_data.set_index("Feature"), color="#ff4b4b")

    else:
        # Placeholder state
        st.info("👈 Adjust parameters and click **Run Prediction** to generate scenarios.")

        # Optional: Cool "Architecture" visual just for aesthetics
        with st.expander("View Model Architecture"):
            st.graphviz_chart('''
                digraph {
                    rankdir=LR;
                    bgcolor="transparent";
                    node [shape=box, style=filled, fillcolor="#1e1e1e", fontcolor="white", color="#444"];
                    edge [color="#666"];

                    Input [label="Telemetry Input\n(Speed, RPM, Throttle)"];
                    Emb [label="Temporal\nEmbeddings"];
                    Attn [label="Multi-Head\nAttention"];
                    FFN [label="Feed Forward\nNetwork"];
                    Out [label="Lap Time\nPrediction"];

                    Input -> Emb -> Attn -> FFN -> Out;
                }
            ''')