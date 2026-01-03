import streamlit as st
import matplotlib.pyplot as plt
import fastf1.plotting
import numpy as np


def render_telemetry_view(session):
    st.subheader("Driver Comparison")

    # 1. Driver Selection
    try:
        driver_map = session.results.set_index('Abbreviation')['FullName'].to_dict()
        drivers_list = list(driver_map.keys())
    except:
        st.error("No driver data found.")
        return

    # Layout: Drivers | Channel | Corner (New!)
    col_sel1, col_sel2, col_sel3 = st.columns([2, 1, 1])

    with col_sel1:
        default_sel = drivers_list[:2] if len(drivers_list) >= 2 else drivers_list[:1]
        drivers = st.multiselect("Select Drivers", drivers_list, default=default_sel)

    with col_sel2:
        telemetry_channel = st.selectbox(
            "Channel",
            ["Speed", "Throttle", "Brake", "RPM", "nGear", "DRS"],
            index=0
        )

    # --- NEW: CORNER ANALYSIS SELECTOR ---
    with col_sel3:
        # Attempt to get circuit info (Turns and their distances)
        try:
            circuit_info = session.get_circuit_info()
            # Create a list like ["Full Lap", "Turn 1", "Turn 2", ...]
            if circuit_info is not None:
                turn_options = ["Full Lap"] + [f"Turn {row['Number']}{row['Letter']}" for _, row in
                                               circuit_info.corners.iterrows()]
            else:
                turn_options = ["Full Lap"]
        except:
            circuit_info = None
            turn_options = ["Full Lap"]

        selected_corner = st.selectbox("Corner Focus", turn_options)

    if drivers:
        fig, ax = plt.subplots(figsize=(10, 5))

        # Dark mode styling
        fig.patch.set_facecolor('none')
        ax.set_facecolor('#0E1117')

        # Track max/min distance for "Full Lap" scaling
        max_distance = 0

        for driver_abbr in drivers:
            try:
                driver_laps = session.laps.pick_driver(driver_abbr)
                if driver_laps.empty:
                    continue

                fastest = driver_laps.pick_fastest()
                telemetry = fastest.get_car_data().add_distance()

                # Update max distance
                max_distance = max(max_distance, telemetry['Distance'].max())

                # Use FastF1 Team Colors
                team_color = fastf1.plotting.get_team_color(fastest['Team'], session=session)

                # Plot selected channel
                ax.plot(telemetry['Distance'], telemetry[telemetry_channel],
                        label=driver_abbr, color=team_color, linewidth=2)
            except:
                pass

        # --- APPLY CORNER ZOOM ---
        if selected_corner != "Full Lap" and circuit_info is not None:
            # Parse "Turn 1" -> get the number/letter
            turn_label = selected_corner.replace("Turn ", "")

            # Find the row in circuit_info
            # We match mostly on Number. Letter handles things like "14a"
            corner_data = circuit_info.corners[
                circuit_info.corners['Number'].astype(str) + circuit_info.corners['Letter'] == turn_label]

            if not corner_data.empty:
                center_dist = corner_data.iloc[0]['Distance']

                # Zoom Window: 400m before apex to 400m after apex
                zoom_start = max(0, center_dist - 400)
                zoom_end = min(max_distance, center_dist + 400)

                ax.set_xlim(zoom_start, zoom_end)

                # Draw a vertical line at the exact Apex distance
                ax.axvline(center_dist, color='white', linestyle=':', alpha=0.3, label="Apex")
                ax.text(center_dist, ax.get_ylim()[1], "APEX", color='white', fontsize=8, alpha=0.5, ha='center')

        # Dynamic labeling based on selection
        units = {
            "Speed": "km/h", "Throttle": "%", "Brake": "%",
            "RPM": "rpm", "nGear": "Gear #", "DRS": "Status"
        }

        ax.set_ylabel(f"{telemetry_channel} ({units.get(telemetry_channel, '')})", color='white')
        ax.set_xlabel("Distance (m)", color='white')

        # Style the grid and ticks for dark mode
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='#333333')

        # Custom legend
        legend = ax.legend(frameon=True, facecolor='#1e1e1e', edgecolor='#333')
        for text in legend.get_texts():
            text.set_color("white")

        st.pyplot(fig)

        # Helper Text
        if selected_corner != "Full Lap":
            st.info(f"🔎 **Zoomed in on {selected_corner}:** Analyzing braking zone and corner exit (±400m).")