import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import fastf1.plotting
import numpy as np


def plot_track_heatmap(session, driver, channel):
    """
    Plots the track map colored by a specific telemetry channel (Speed, Gear, Brake, etc.)
    """
    try:
        lap = session.laps.pick_driver(driver).pick_fastest()
        if lap is None:
            return None

        telemetry = lap.get_telemetry()

        x = telemetry['X'].values
        y = telemetry['Y'].values

        if channel == "Speed":
            z = telemetry['Speed']
            label = "Speed (km/h)"
            cmap = 'plasma'
        elif channel == "Gear":
            z = telemetry['nGear']
            label = "Gear"
            cmap = 'Paired'
        elif channel == "Brake":
            z = telemetry['Brake']
            label = "Brake (%)"
            cmap = 'Reds'
        elif channel == "RPM":
            z = telemetry['RPM']
            label = "RPM"
            cmap = 'viridis'
        else:
            z = telemetry['Speed']
            label = "Speed"
            cmap = 'plasma'

        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')

        norm = plt.Normalize(z.min(), z.max())
        lc = LineCollection(segments, cmap=cmap, norm=norm, linestyle='-', linewidth=5)
        lc.set_array(z)
        line = ax.add_collection(lc)

        ax.set_xlim(x.min() - 200, x.max() + 200)
        ax.set_ylim(y.min() - 200, y.max() + 200)
        ax.axis('off')
        ax.set_aspect('equal')

        cbar = fig.colorbar(line, ax=ax, shrink=0.7, pad=0.05, location='bottom')
        cbar.set_label(label, color='white', fontsize=10)
        cbar.ax.xaxis.set_tick_params(color='white') 
        plt.setp(plt.getp(cbar.ax.axes, 'xticklabels'), color='white')

        ax.set_title(f"{driver}", color='white', fontsize=14, fontweight='bold')

        return fig

    except Exception as e:
        st.error(f"Error plotting heatmap for {driver}: {e}")
        return None

@st.dialog("🗺️ Track Map Heatmaps", width="large")
def show_heatmap_dialog(session, drivers, channel):
    st.markdown(f"Comparing **{channel}** across selected drivers.")

    cols_per_row = 5

    for i in range(0, len(drivers), cols_per_row):
        cols = st.columns(cols_per_row)

        batch = drivers[i: i + cols_per_row]

        for j, driver_abbr in enumerate(batch):
            with cols[j]:
                with st.spinner(f"Loading {driver_abbr}..."):
                    fig_map = plot_track_heatmap(session, driver_abbr, channel)
                    if fig_map:
                        st.pyplot(fig_map, use_container_width=True)


def render_telemetry_view(session):
    st.subheader("Driver Comparison")

    try:
        driver_map = session.results.set_index('Abbreviation')['FullName'].to_dict()
        drivers_list = list(driver_map.keys())
    except:
        st.error("No driver data found.")
        return

    col_sel1, col_sel2, col_sel3, col_sel4 = st.columns([2, 1, 1, 0.8], vertical_alignment="bottom")

    with col_sel1:
        default_sel = drivers_list[:2] if len(drivers_list) >= 2 else drivers_list[:1]
        drivers = st.multiselect("Select Drivers", drivers_list, default=default_sel)

    with col_sel2:
        telemetry_channel = st.selectbox(
            "Channel",
            ["Speed", "Throttle", "Brake", "RPM", "nGear", "DRS"],
            index=0
        )

    with col_sel3:
        try:
            circuit_info = session.get_circuit_info()
            if circuit_info is not None:
                turn_options = ["Full Lap"] + [f"Turn {row['Number']}{row['Letter']}" for _, row in
                                               circuit_info.corners.iterrows()]
            else:
                turn_options = ["Full Lap"]
        except:
            circuit_info = None
            turn_options = ["Full Lap"]

        selected_corner = st.selectbox("Corner Focus", turn_options)

    with col_sel4:
        st.write('') 
        if st.button("🗺️ Heatmaps", help="View track map comparison", use_container_width=True):
            if drivers:
                show_heatmap_dialog(session, drivers, telemetry_channel)
            else:
                st.warning("Select drivers first!")

    if drivers:
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('none')
        ax.set_facecolor('#0E1117')

        max_distance = 0

        for driver_abbr in drivers:
            try:
                driver_laps = session.laps.pick_driver(driver_abbr)
                if driver_laps.empty:
                    continue

                fastest = driver_laps.pick_fastest()
                telemetry = fastest.get_car_data().add_distance()

                max_distance = max(max_distance, telemetry['Distance'].max())
                team_color = fastf1.plotting.get_team_color(fastest['Team'], session=session)

                ax.plot(telemetry['Distance'], telemetry[telemetry_channel],
                        label=driver_abbr, color=team_color, linewidth=2)
            except:
                pass

        if selected_corner != "Full Lap" and circuit_info is not None:
            turn_label = selected_corner.replace("Turn ", "")
            corner_data = circuit_info.corners[
                circuit_info.corners['Number'].astype(str) + circuit_info.corners['Letter'] == turn_label]

            if not corner_data.empty:
                center_dist = corner_data.iloc[0]['Distance']
                zoom_start = max(0, center_dist - 400)
                zoom_end = min(max_distance, center_dist + 400)
                ax.set_xlim(zoom_start, zoom_end)
                ax.axvline(center_dist, color='white', linestyle=':', alpha=0.3, label="Apex")
                ax.text(center_dist, ax.get_ylim()[1], "APEX", color='white', fontsize=8, alpha=0.5, ha='center')

        units = {"Speed": "km/h", "Throttle": "%", "Brake": "%", "RPM": "rpm", "nGear": "Gear #", "DRS": "Status"}
        ax.set_ylabel(f"{telemetry_channel} ({units.get(telemetry_channel, '')})", color='white')
        ax.set_xlabel("Distance (m)", color='white')
        ax.tick_params(colors='white')
        ax.grid(True, linestyle='--', linewidth=0.5, color='#333333')

        legend = ax.legend(frameon=True, facecolor='#1e1e1e', edgecolor='#333')
        for text in legend.get_texts():
            text.set_color("white")

        st.pyplot(fig)

        if selected_corner != "Full Lap" and circuit_info is not None:
            st.info(f"🔎 **Zoomed in on {selected_corner}:** Analyzing braking zone and corner exit (±400m).")

            turn_label = selected_corner.replace("Turn ", "")
            corner_row = circuit_info.corners[
                circuit_info.corners['Number'].astype(str) + circuit_info.corners['Letter'] == turn_label
                ]

            if not corner_row.empty:
                apex_dist = corner_row.iloc[0]['Distance']

                corner_stats = []

                for driver in drivers:
                    try:
                        laps = session.laps.pick_driver(driver).pick_fastest()
                        car_data = laps.get_car_data().add_distance()

                        apex_zone = car_data[
                            (car_data['Distance'] > apex_dist - 50) & (car_data['Distance'] < apex_dist + 50)]
                        min_speed = apex_zone['Speed'].min()

                        entry_zone = car_data.iloc[(car_data['Distance'] - (apex_dist - 100)).abs().argsort()[:1]]
                        entry_speed = entry_zone['Speed'].values[0] if not entry_zone.empty else 0

                        exit_zone = car_data.iloc[(car_data['Distance'] - (apex_dist + 100)).abs().argsort()[:1]]
                        exit_speed = exit_zone['Speed'].values[0] if not exit_zone.empty else 0

                        corner_stats.append({
                            "Driver": driver,
                            "Entry Speed (km/h)": round(entry_speed, 1),
                            "Apex Speed (km/h)": round(min_speed, 1),
                            "Exit Speed (km/h)": round(exit_speed, 1)
                        })
                    except Exception:
                        pass

                if corner_stats:
                    st.write("#### ⚡ Corner Performance Metrics")
                    st.dataframe(
                        corner_stats,
                        hide_index=True,
                        use_container_width=True
                    )

        if selected_corner != "Full Lap":
            st.info(f"🔎 **Zoomed in on {selected_corner}:** Analyzing braking zone and corner exit (±400m).")
