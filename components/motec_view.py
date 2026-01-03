import streamlit as st
import pandas as pd
from io import BytesIO


# --- HELPER: INSTRUCTIONS DIALOG ---
@st.dialog("🎮 Sim Racing Guide")
def show_motec_guide():
    st.markdown("""
    ### How to Race Against the Pros

    This tool exports real F1 telemetry into a format compatible with **MoTeC i2 Pro**, allowing you to compare your Assetto Corsa laps against the real pole position data.

    #### 1. The Setup
    * **Assetto Corsa:** You need the **ACTI** (Assetto Corsa Telemetry Interface) mod installed.
    * **MoTeC i2 Pro:** Download the free analysis software from MoTeC.

    #### 2. The Workflow
    1.  **Record Your Lap:** Drive a clean lap in Assetto Corsa. ACTI will save a log file.
    2.  **Export F1 Data:** Use this app to download the CSV for your target driver (e.g., Max Verstappen).
    3.  **Import to MoTeC:** * Open MoTeC i2 Pro.
        * Go to `File > Import` and select the F1 CSV you just downloaded.
        * Then open your own ACTI log file in the same workspace.

    #### 3. The Comparison
    * You will now see two lines on your telemetry graphs.
    * **Red Line:** Real F1 Driver (Reference).
    * **Green Line:** You.
    * Use the **Time Difference** channel to see exactly where you are losing time (braking too early, corner speed, etc.).
    """)


# --- HELPER CLASS: EXPORTER ---
class MotecExporter:
    def __init__(self, session):
        self.session = session

    def generate_motec_csv(self, driver, lap_number=None):
        laps = self.session.laps.pick_driver(driver)
        if lap_number:
            lap = laps[laps['LapNumber'] == lap_number].iloc[0]
        else:
            lap = laps.pick_fastest()

        # Telemetry processing
        telemetry = lap.get_car_data().add_distance().add_relative_distance()

        # Resample to 60Hz
        t_start = telemetry['Time'].min()
        t_end = telemetry['Time'].max()
        new_time_index = pd.timedelta_range(start=t_start, end=t_end, freq='16ms')

        telemetry = telemetry.set_index('Time')
        telemetry_resampled = telemetry.reindex(new_time_index).interpolate(method='linear')
        telemetry_resampled = telemetry_resampled.reset_index().rename(columns={'index': 'Time'})

        col_mapping = {
            'Time': 'Time', 'Distance': 'Distance', 'Speed': 'Ground Speed',
            'RPM': 'Engine RPM', 'nGear': 'Gear', 'Throttle': 'Throttle Pos',
            'Brake': 'Brake Pos', 'DRS': 'DRS Status'
        }
        final_df = telemetry_resampled[list(col_mapping.keys())].rename(columns=col_mapping)
        final_df['Time'] = final_df['Time'].dt.total_seconds()
        final_df['Time'] = final_df['Time'] - final_df['Time'].iloc[0]

        csv_buffer = BytesIO()

        # Header construction
        header = [
            f'"Format","MoTeC CSV 1.1"',
            f'"Venue","{self.session.event.EventName}"',
            f'"Vehicle","{lap["Team"]}"',
            f'"Driver","{driver}"',
            f'"Device","FastF1 Export"',
            f'"Comment","Lap {int(lap["LapNumber"])}"',
            f'"Date","{self.session.date.strftime("%Y-%m-%d")}"',
            f'"Time","{self.session.date.strftime("%H:%M:%S")}"',
            f'"Sample Rate","60"',
            f'"Duration","{final_df["Time"].max():.3f}"',
            f'"Range Field","Time"',
            f'"Volume",""', f'"Excld",""', f'"Driver Separator","1"', ''
        ]
        csv_buffer.write(('\n'.join(header) + '\n').encode('utf-8'))

        units = {'Time': 's', 'Distance': 'm', 'Ground Speed': 'kph', 'Engine RPM': 'rpm',
                 'Gear': '', 'Throttle Pos': '%', 'Brake Pos': '%', 'DRS Status': ''}
        unit_row = [units[col] for col in final_df.columns]

        cols_str = '"' + '","'.join(final_df.columns) + '"\n'
        units_str = '"' + '","'.join(unit_row) + '"\n'

        csv_buffer.write(cols_str.encode('utf-8'))
        csv_buffer.write(units_str.encode('utf-8'))
        final_df.to_csv(csv_buffer, header=False, index=False, float_format='%.3f')
        csv_buffer.seek(0)
        return csv_buffer


# --- UI RENDERER ---
def render_motec_view(session):
    st.subheader("Assetto Corsa / MoTeC Exporter")

    # Header with Info Button
    col_head1, col_head2 = st.columns([0.85, 0.15])
    with col_head1:
        st.markdown("Export telemetry to compare your Sim Racing laps against real F1 data in **MoTeC i2 Pro**.")
    with col_head2:
        if st.button("ℹ️ Help"):
            show_motec_guide()

    # 1. Load Drivers
    try:
        driver_map = session.results.set_index('FullName')['Abbreviation'].to_dict()
        driver_names = sorted(list(driver_map.keys()))
    except:
        st.error("Driver data not available for this session.")
        return

    # 2. Driver Selection (Defaults to None to trigger warning)
    col1, col2 = st.columns(2)

    with col1:
        sel_driver_name = st.selectbox(
            "Select Driver",
            driver_names,
            index=None,
            placeholder="Choose a driver..."
        )

    # 3. Logic Flow
    if sel_driver_name is None:
        # State A: No driver selected -> Show Warning
        st.warning("👈 Please select a driver to view their lap times and generate data.")

    else:
        # State B: Driver selected -> Show Stats & Export Tools
        ex_driver_code = driver_map.get(sel_driver_name, None)

        if ex_driver_code:
            driver_laps = session.laps.pick_driver(ex_driver_code).copy()
            driver_laps = driver_laps.loc[:, ~driver_laps.columns.duplicated()]

            # --- KEY FEATURE: Identify Best Lap ---
            try:
                fastest_lap = driver_laps.pick_fastest()
                fastest_lap_num = int(fastest_lap['LapNumber'])
                fastest_lap_time = str(fastest_lap['LapTime']).split('days')[-1][:-3]  # Format: 00:01:23.456

                # Show dynamic info box
                st.info(f"🏎️ **Best Lap for {sel_driver_name}:** Lap {fastest_lap_num} ({fastest_lap_time})")
            except:
                st.warning("Could not determine fastest lap.")
                fastest_lap_num = -1

            # Format labels for dropdown
            driver_laps['Label'] = driver_laps.apply(
                lambda x: f"Lap {int(x['LapNumber'])} - {str(x['LapTime']).split('days')[-1][:-3]}",
                axis=1
            )

            # Find the index of the fastest lap to set as default
            fastest_lap_idx = 0
            if fastest_lap_num != -1:
                match = driver_laps.index[driver_laps['LapNumber'] == fastest_lap_num].tolist()
                if match:
                    fastest_lap_idx = driver_laps.reset_index().index[driver_laps['LapNumber'] == fastest_lap_num][0]

            with col2:
                sel_lap_label = st.selectbox(
                    "Select Lap",
                    driver_laps['Label'],
                    index=int(fastest_lap_idx)  # Auto-select the fastest lap
                )

                if sel_lap_label:
                    sel_lap_num = int(sel_lap_label.split(' ')[1])
                else:
                    sel_lap_num = None

            # Generate Button
            st.write("")  # Spacer
            if st.button("Generate MoTeC CSV", type="primary"):
                if sel_lap_num:
                    with st.spinner(f"Exporting {sel_driver_name} - Lap {sel_lap_num}..."):
                        exporter = MotecExporter(session)
                        csv_data = exporter.generate_motec_csv(ex_driver_code, sel_lap_num)

                        if csv_data:
                            file_name = f"{session.event.EventName}_{ex_driver_code}_Lap{sel_lap_num}.csv"
                            st.download_button(
                                label="Download CSV File",
                                data=csv_data,
                                file_name=file_name,
                                mime="text/csv"
                            )
                            st.success(f"✅ Export Complete! File: `{file_name}`")