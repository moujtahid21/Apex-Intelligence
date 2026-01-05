import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import fastf1.plotting
import numpy as np


# --- HELPER: TRACK HEATMAP PLOTTER ---
def plot_track_heatmap(session, driver, channel):
    """
    Plots the track map colored by a specific telemetry channel (Speed, Gear, Brake, etc.)
    """
    try:
        # Get fastest lap telemetry
        lap = session.laps.pick_driver(driver).pick_fastest()
        if lap is None:
            return None

        telemetry = lap.get_telemetry()

        # Prepare Data
        x = telemetry['X'].values
        y = telemetry['Y'].values

        # Select data based on channel
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

        # Create Line Segments for Color Mapping
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # Plot settings
        # We make the figure square-ish to fit better in grid cards
        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')

        # Create Line Collection
        norm = plt.Normalize(z.min(), z.max())
        lc = LineCollection(segments, cmap=cmap, norm=norm, linestyle='-', linewidth=5)
        lc.set_array(z)
        line = ax.add_collection(lc)

        # Map bounds
        ax.set_xlim(x.min() - 200, x.max() + 200)
        ax.set_ylim(y.min() - 200, y.max() + 200)
        ax.axis('off')
        ax.set_aspect('equal')

        # Colorbar
        cbar = fig.colorbar(line, ax=ax, shrink=0.7, pad=0.05, location='bottom')
        cbar.set_label(label, color='white', fontsize=10)
        cbar.ax.xaxis.set_tick_params(color='white')  # Bottom colorbar uses xaxis
        plt.setp(plt.getp(cbar.ax.axes, 'xticklabels'), color='white')

        # Title
        ax.set_title(f"{driver}", color='white', fontsize=14, fontweight='bold')

        return fig

    except Exception as e:
        st.error(f"Error plotting heatmap for {driver}: {e}")
        return None


# --- HELPER: POPUP DIALOG ---
@st.dialog("🗺️ Track Map Heatmaps", width="large")
def show_heatmap_dialog(session, drivers, channel):
    st.markdown(f"Comparing **{channel}** across selected drivers.")

    # Grid Logic: 5 Drivers per row
    cols_per_row = 5

    # Loop through drivers in chunks of 5
    for i in range(0, len(drivers), cols_per_row):
        # Create a new row of columns
        cols = st.columns(cols_per_row)

        # Get the batch of up to 5 drivers
        batch = drivers[i: i + cols_per_row]

        for j, driver_abbr in enumerate(batch):
            with cols[j]:
                with st.spinner(f"Loading {driver_abbr}..."):
                    fig_map = plot_track_heatmap(session, driver_abbr, channel)
                    if fig_map:
                        st.pyplot(fig_map, use_container_width=True)


# --- MAIN RENDER FUNCTION ---
def render_telemetry_view(session):
    st.subheader("Driver Comparison")

    # 1. Driver Selection
    try:
        driver_map = session.results.set_index('Abbreviation')['FullName'].to_dict()
        drivers_list = list(driver_map.keys())
    except:
        st.error("No driver data found.")
        return

    # Layout: Drivers | Channel | Corner | Heatmap Button
    # Adjusted ratios to fit the button comfortably
    col_sel1, col_sel2, col_sel3, col_sel4 = st.columns([2, 1, 1, 0.8])

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

    # --- BUTTON TO TRIGGER POPUP ---
    with col_sel4:
        st.write("")  # Spacer to align button with dropdowns
        st.write("")
        if st.button("🗺️ Heatmaps", help="View track map comparison", use_container_width=True):
            if drivers:
                show_heatmap_dialog(session, drivers, telemetry_channel)
            else:
                st.warning("Select drivers first!")

    # --- MAIN LINE CHART (Always Visible) ---
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

        # Apply Corner Zoom
        if selected_corner != "Full Lap" and circuit_info is not None:
            turn_label = selected_corner.replace("Turn ", "")
            # Robust matching for turn labels (handles "1" vs "01" string issues)
            corner_data = circuit_info.corners[
                circuit_info.corners['Number'].astype(str) + circuit_info.corners['Letter'] == turn_label]

            if not corner_data.empty:
                center_dist = corner_data.iloc[0]['Distance']
                zoom_start = max(0, center_dist - 400)
                zoom_end = min(max_distance, center_dist + 400)
                ax.set_xlim(zoom_start, zoom_end)
                ax.axvline(center_dist, color='white', linestyle=':', alpha=0.3, label="Apex")
                ax.text(center_dist, ax.get_ylim()[1], "APEX", color='white', fontsize=8, alpha=0.5, ha='center')

        # Styling
        units = {"Speed": "km/h", "Throttle": "%", "Brake": "%", "RPM": "rpm", "nGear": "Gear #", "DRS": "Status"}
        ax.set_ylabel(f"{telemetry_channel} ({units.get(telemetry_channel, '')})", color='white')
        ax.set_xlabel("Distance (m)", color='white')
        ax.tick_params(colors='white')
        ax.grid(True, linestyle='--', linewidth=0.5, color='#333333')

        legend = ax.legend(frameon=True, facecolor='#1e1e1e', edgecolor='#333')
        for text in legend.get_texts():
            text.set_color("white")

        st.pyplot(fig)

        if selected_corner != "Full Lap":
            st.info(f"🔎 **Zoomed in on {selected_corner}:** Analyzing braking zone and corner exit (±400m).")