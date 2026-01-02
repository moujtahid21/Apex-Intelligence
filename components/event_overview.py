import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import fastf1
import fastf1.plotting
from PIL import Image
import os
import base64  # Added for image encoding


def crop_to_face(image_path):
    """
    Crops the top 20% of a tall portrait image to focus on the face.
    """
    try:
        img = Image.open(image_path)
        width, height = img.size

        # Crop logic for F1 portrait photos
        target_height = int(width * 0.85)
        img_cropped = img.crop((0, 0, width, target_height))
        return img_cropped
    except Exception as e:
        return None


def get_img_as_base64(file_path):
    """
    Reads an image file and converts it to a base64 string for HTML embedding.
    """
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def render_event_overview(session):
    """
    Renders the metrics and track map for Tab 1 with a dashboard layout.
    """
    # --- 1. DATA PREPARATION ---
    try:
        fastest_lap = session.laps.pick_fastest()
        telemetry = fastest_lap.get_car_data().add_distance()
        circuit_length_km = telemetry['Distance'].max() / 1000
        lap_time_str = str(fastest_lap['LapTime']).split('days')[-1][:-3]

        try:
            weather = session.weather_data.iloc[
                session.weather_data.index.get_indexer([fastest_lap['Time']], method='nearest')]
            track_temp = f"{weather['TrackTemp'].values[0]} °C"
            air_temp = f"{weather['AirTemp'].values[0]} °C"
            humidity = f"{weather['Humidity'].values[0]} %"
        except:
            track_temp = "N/A"
            air_temp = "N/A"
            humidity = "N/A"

        driver_code = fastest_lap['Driver']
        team_name = fastest_lap['Team']
        try:
            driver_info = session.results.loc[session.results['Abbreviation'] == driver_code].iloc[0]
            full_name = driver_info['FullName']
        except:
            full_name = driver_code

    except Exception as e:
        st.error(f"Error loading metrics: {e}")
        return

    # --- 2. HEADER & METRICS ROW ---
    st.subheader(f"📍 {session.event.EventName} - {session.name}")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Track Temp", track_temp)
    m2.metric("Air Temp", air_temp)
    m3.metric("Humidity", humidity)
    m4.metric("Circuit Length", f"{circuit_length_km:.3f} km")

    # --- 5. CUSTOM METRIC FOR TYRE ---
    with m5:
        # We use custom HTML to align the image perfectly with the text label
        # This removes the standard Streamlit widget gap
        compound = fastest_lap['Compound'].upper()

        tyre_assets = {
            "SOFT": "assets/tires/F1_tire_Pirelli_PZero_Red_18.svg",
            "MEDIUM": "assets/tires/F1_tire_Pirelli_PZero_Yellow_18.svg",
            "HARD": "assets/tires/F1_tire_Pirelli_PZero_White_18.svg",
            "INTERMEDIATE": "assets/tires/F1_tire_Pirelli_Cinturato_Green_18.svg",
            "WET": "assets/tires/F1_tire_Pirelli_Cinturato_Blue_18.svg"
        }

        img_path = tyre_assets.get(compound, None)
        b64_img = get_img_as_base64(img_path) if img_path else None

        if b64_img:
            # HTML Block to mimic st.metric look but with an image value
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; justify-content: flex-start;">
                    <p style="font-size: 14px; color: rgba(250, 250, 250, 1.0); margin-bottom: 5px;">Fastest Tyre</p>
                    <div style="height: 35px; display: flex; align-items: center;">
                        <img src="data:image/svg+xml;base64,{b64_img}" style="max-height: 100%; width: auto;">
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.metric("Fastest Tyre", compound)

    st.divider()

    # --- 3. MAIN CONTENT ---
    col_driver, col_map = st.columns([1, 2.5])

    with col_driver:
        with st.container(border=True):
            st.markdown("#### 🏆 Fastest Lap")
            image_path = f"assets/drivers/{driver_code}.png"

            if os.path.exists(image_path):
                cropped_img = crop_to_face(image_path)
                st.image(cropped_img, use_container_width=True)
            else:
                st.image("https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png",
                         use_container_width=True)

            st.markdown(f"""
            <div style='text-align: center;'>
                <h1 style='margin:0; padding:0; font-size: 1.5rem; color: #ff1801;'>{lap_time_str}</h1>
                <h3 style='margin:0; padding:0;'>{full_name}</h3>
                <p style='color: #888;'>{team_name}</p>
            </div>
            """, unsafe_allow_html=True)

    with col_map:
        try:
            circuit_info = session.get_circuit_info()
            render_enhanced_track_map(session, fastest_lap, circuit_info)
        except Exception as e:
            st.error(f"Could not render map: {e}")


def render_enhanced_track_map(session, lap, circuit_info):
    """
    Draws the track map with Turn Numbers.
    """
    pos = lap.get_pos_data()
    fig, ax = plt.subplots(figsize=(12, 7))

    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')

    track = pos.loc[:, ('X', 'Y')].to_numpy()

    track_angle = 0
    if circuit_info is not None:
        track_angle = circuit_info.rotation / 180 * np.pi

    def rotate(xy, angle):
        rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                            [-np.sin(angle), np.cos(angle)]])
        return np.matmul(xy, rot_mat)

    if track_angle != 0:
        track = rotate(track, angle=track_angle)

    ax.plot(track[:, 0], track[:, 1], color='#FF1801', linewidth=4, zorder=1)

    if circuit_info is not None:
        offset_vector = [500, 0]
        for _, corner in circuit_info.corners.iterrows():
            txt = f"{corner['Number']}{corner['Letter']}"
            corner_angle = corner['Angle'] / 180 * np.pi
            offset_x, offset_y = rotate(offset_vector, angle=corner_angle)
            text_x = corner['X'] + offset_x
            text_y = corner['Y'] + offset_y
            text_x, text_y = rotate([text_x, text_y], angle=track_angle)

            ax.scatter(text_x, text_y, color='#1e1e1e', s=120, edgecolor='#888', zorder=2)
            ax.text(text_x, text_y, txt,
                    color='white', fontsize=9, fontweight='bold',
                    ha='center', va='center', zorder=3)

    ax.set_aspect('equal')
    ax.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    st.pyplot(fig)