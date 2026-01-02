import streamlit as st
import matplotlib.pyplot as plt
import fastf1
import fastf1.plotting
from components.tyre_legend import TyreLegend


# --- HELPER: STRATEGY INFO CARD ---
@st.dialog("🏁 Tyre Strategy Guide")
def show_strategy_card():
    # CSS to reduce padding inside the modal for a tighter fit
    st.markdown("""
        <style>
            div[data-testid="stMarkdownContainer"] p {
                margin-bottom: 0.5rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    **F1 strategy is a high-speed chess game balancing speed vs. durability.**

    Teams analyze "degradation" (wear) to decide the perfect lap to pit.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        🔴 **SOFT** *Fastest but fragile.* High grip, high wear.  
        *Best for:* Qualifying, Starts.
        """)

        st.markdown("""
        ⚪ **HARD** *Durable but slower.* Low wear, hard to warm up.  
        *Best for:* Long race stints.
        """)

    with col2:
        st.markdown("""
        🟡 **MEDIUM** *The Balanced Choice.* Compromise of speed & life.  
        *Best for:* Core race strategy.
        """)

        st.markdown("""
        🟢 **INTER / WET** 🔵  
        *Rain Masters.* Grooved to displace water.  
        *Best for:* Damp to Heavy Rain.
        """)

    st.info("💡 **Winning Move:** Reacting to tire wear faster than the car behind you.")


def render_strategy_view(session):
    """
    Renders the Tyre Strategy Stint Chart + Legend + Info Card
    """
    st.subheader("Tyre Strategy & Stints")

    # --- 1. PLOT GENERATION ---
    # We use a Spinner because plotting all stints can take a second
    with st.spinner("Analyzing tyre history..."):
        fig, ax = plt.subplots(figsize=(10, 6))

        # Dark Mode Plot Styling
        fig.patch.set_facecolor('none')
        ax.set_facecolor('#0E1117')

        # Filter for top 5 drivers to keep chart readable
        # (You can change this to 20 to see everyone)
        top_drivers = session.results.iloc[:5]['Abbreviation']

        for driver_idx, driver in enumerate(top_drivers):
            driver_laps = session.laps.pick_driver(driver)

            # Group by Stint (continuous period on one set of tires)
            for stint_number, stint in driver_laps.groupby('Stint'):
                compound = stint['Compound'].iloc[0]

                # Get Official Color
                color = fastf1.plotting.get_compound_color(compound, session=session)

                # Calculate Bar Dimensions
                start_lap = stint['LapNumber'].min()
                end_lap = stint['LapNumber'].max()
                duration = end_lap - start_lap + 1

                # Plot the Bar
                # height=0.6 makes the bars thinner and sleeker
                ax.barh(driver, duration, left=start_lap, color=color, edgecolor='#111', height=0.6)

                # Add Text Label inside the bar if it's wide enough
                if duration > 3:
                    midpoint = start_lap + (duration / 2)
                    label = compound[0] if compound else "?"
                    ax.text(midpoint, driver_idx, label,
                            va='center', ha='center', color='black' if compound in ['HARD', 'MEDIUM'] else 'white',
                            fontweight='bold', fontsize=8)

        ax.set_xlabel("Lap Number", color='white')
        ax.invert_yaxis()  # Put P1 at the top

        # Remove borders for a cleaner look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#333')

        # Grid settings
        ax.grid(axis='x', linestyle=':', alpha=0.3, color='white')

        # Tick colors
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        st.pyplot(fig)

    # --- 2. CUSTOM LEGEND ---
    st.markdown("### Tyre Compound Legend")

    # Define Assets
    tyre_assets = {
        "SOFT": "assets/tires/F1_tire_Pirelli_PZero_Red_18.svg",
        "MEDIUM": "assets/tires/F1_tire_Pirelli_PZero_Yellow_18.svg",
        "HARD": "assets/tires/F1_tire_Pirelli_PZero_White_18.svg",
        "INTERMEDIATE": "assets/tires/F1_tire_Pirelli_Cinturato_Green_18.svg",
        "WET": "assets/tires/F1_tire_Pirelli_Cinturato_Blue_18.svg"
    }

    compounds_data = [
        ("SOFT", "Fastest, High Degradation"),
        ("MEDIUM", "Balanced"),
        ("HARD", "Durable, Low Degradation"),
        ("INTERMEDIATE", "Light Rain / Damp"),
        ("WET", "Heavy Rain")
    ]

    # Render the HTML Component
    # height=75 removes the gap we fixed earlier
    legend = TyreLegend(compounds=compounds_data, assets=tyre_assets, height=75)
    legend.show()

    # --- 3. INFO BUTTON ---
    if st.button("ℹ️ Strategy Info"):
        show_strategy_card()