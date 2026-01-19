import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import fastf1
import fastf1.plotting
import os


from utils.helpers import (
    crop_to_face,
    get_img_as_base64,
    calculate_tyre_health,
    calculate_driver_rating
)

from components.driver_card import render_driver_card


def render_event_overview(session):
    try:
        fastest_lap = session.laps.pick_fastest()
        telemetry = fastest_lap.get_car_data().add_distance()
        circuit_length_km = telemetry['Distance'].max() / 1000
        lap_time_str = str(fastest_lap['LapTime']).split('days')[-1][:-3]


        try:
            weather_data = session.laps.get_weather_data()

            weather_row = weather_data.loc[fastest_lap.name]

            track_temp = f"{weather_row['TrackTemp']} °C"
            air_temp = f"{weather_row['AirTemp']} °C"
            humidity = f"{weather_row['Humidity']} %"
        except Exception as e:
            track_temp = "N/A"
            air_temp = "N/A"
            humidity = "N/A"
            print(f"Weather Error: {e}")

        driver_code = fastest_lap['Driver']
        team_name = fastest_lap['Team']
        try:
            driver_info = session.results.loc[session.results['Abbreviation'] == driver_code].iloc[0]
            full_name = driver_info['FullName']
        except:
            full_name = driver_code

        tyre_health, deg_msg = calculate_tyre_health(session, fastest_lap)
        driver_rating = calculate_driver_rating(session, driver_code)

    except Exception as e:
        st.error(f"Error loading metrics: {e}")
        return

    st.subheader(f"📍 {session.event.EventName} - {session.name}")

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Track Temp", track_temp)
    m2.metric("Air Temp", air_temp)
    m3.metric("Humidity", humidity)
    m4.metric("Circuit Length", f"{circuit_length_km:.3f} km")

    with m5:
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

    with m6:
        st.metric("Tyre Health", f"{tyre_health}%", delta=deg_msg, delta_color="inverse")

    st.divider()

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

            render_driver_card(lap_time_str, full_name, team_name, driver_rating)

    with col_map:
        try:
            circuit_info = session.get_circuit_info()
            render_enhanced_track_map(session, fastest_lap, circuit_info)
        except Exception as e:
            st.error(f"Could not render map: {e}")


def render_enhanced_track_map(session, lap, circuit_info):
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

            ax.scatter(text_x, text_y, color='#1e1e1e', s=360, edgecolor='#888', zorder=2)
            ax.text(text_x, text_y, txt,
                    color='white', fontsize=12, fontweight='bold',
                    ha='center', va='center', zorder=3)

    ax.set_aspect('equal')
    ax.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    st.pyplot(fig)
