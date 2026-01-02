import streamlit as st
import matplotlib.pyplot as plt
import fastf1.plotting


def render_telemetry_view(session):
    st.subheader("Driver Comparison")

    # 1. Driver Selection
    try:
        driver_map = session.results.set_index('Abbreviation')['FullName'].to_dict()
        drivers_list = list(driver_map.keys())
    except:
        st.error("No driver data found.")
        return

    col_sel1, col_sel2 = st.columns([3, 1])

    with col_sel1:
        default_sel = drivers_list[:2] if len(drivers_list) >= 2 else drivers_list[:1]
        drivers = st.multiselect("Select Drivers", drivers_list, default=default_sel)

    with col_sel2:
        # ENHANCEMENT: Select which data channel to plot
        telemetry_channel = st.selectbox(
            "Channel",
            ["Speed", "Throttle", "Brake", "RPM", "nGear", "DRS"],
            index=0
        )

    if drivers:
        fig, ax = plt.subplots(figsize=(10, 5))

        # Dark mode styling
        fig.patch.set_facecolor('none')
        ax.set_facecolor('#0E1117')  # Match Streamlit dark bg

        for driver_abbr in drivers:
            try:
                driver_laps = session.laps.pick_driver(driver_abbr)
                if driver_laps.empty:
                    continue

                fastest = driver_laps.pick_fastest()
                telemetry = fastest.get_car_data().add_distance()

                # Use FastF1 Team Colors
                team_color = fastf1.plotting.get_team_color(fastest['Team'], session=session)

                # Plot selected channel
                ax.plot(telemetry['Distance'], telemetry[telemetry_channel],
                        label=driver_abbr, color=team_color, linewidth=2)
            except:
                pass

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