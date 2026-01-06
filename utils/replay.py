import plotly.graph_objects as go
import streamlit as st


def get_replay_explanation():
    """Returns the text for the info box."""
    return """
    **🎮 Replay Controls**
    * **Auto-Play:** Check the box to watch the ghost car battle live.
    * **Manual Scrub:** Uncheck Auto-Play and use the slider to analyze specific corners.
    * **Telemetry:** Bars indicate Throttle (Green) and Brake (Red) intensity.
    """


def create_telemetry_html(driver, speed, gear, throttle, brake, color_code):
    """
    Generates the HTML string for a single driver's telemetry card.
    color_code example: '#FF8000' for McLaren, '#1E41FF' for Red Bull
    """

    # Normalize throttle/brake to percentage width for CSS
    throttle_width = max(0, min(100, throttle))
    brake_width = max(0, min(100, brake))

    throttle_color = "#00ff00"  # Green
    brake_color = "#ff0000"  # Red (Restored as requested)

    html = f"""
    <div style="border: 2px solid {color_code}; border-radius: 8px; padding: 10px; margin-bottom: 10px; background-color: #1e1e1e;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
            <span style="font-size: 1.2em; font-weight: bold; color: {color_code};">{driver}</span>
            <div style="background-color: #333; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold;">
                {int(gear)}
            </div>
        </div>

        <div style="display: flex; align-items: baseline; margin-bottom: 8px;">
            <span style="font-size: 1.8em; font-weight: bold; color: white; margin-right: 5px;">{int(speed)}</span>
            <span style="font-size: 0.8em; color: #888;">KM/H</span>
        </div>

        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <span style="width: 30px; font-size: 0.7em; color: #888;">THR</span>
            <div style="flex-grow: 1; background-color: #333; height: 8px; border-radius: 4px;">
                <div style="width: {throttle_width}%; background-color: {throttle_color}; height: 100%; border-radius: 4px; transition: width 0.1s;"></div>
            </div>
        </div>

        <div style="display: flex; align-items: center;">
            <span style="width: 30px; font-size: 0.7em; color: #888;">BRK</span>
            <div style="flex-grow: 1; background-color: #333; height: 8px; border-radius: 4px;">
                <div style="width: {brake_width}%; background-color: {brake_color}; height: 100%; border-radius: 4px; transition: width 0.1s;"></div>
            </div>
        </div>
    </div>
    """
    return html


def get_track_map_fig(track_df, driver1_pos, driver2_pos):
    """
    Returns a Plotly figure with the track line and two markers for the cars.
    driver_pos format: (x_coordinate, y_coordinate)
    """
    fig = go.Figure()

    # 1. The Static Track Line
    fig.add_trace(go.Scatter(
        x=track_df['x'],
        y=track_df['y'],
        mode='lines',
        line=dict(color='#444', width=4),
        hoverinfo='skip'
    ))

    # 2. Driver 1 Marker (e.g., NOR)
    fig.add_trace(go.Scatter(
        x=[driver1_pos[0]],
        y=[driver1_pos[1]],
        mode='markers',
        marker=dict(size=12, color='#FF8000', symbol='circle'),  # McLaren Orange
        name='NOR'
    ))

    # 3. Driver 2 Marker (e.g., VER)
    fig.add_trace(go.Scatter(
        x=[driver2_pos[0]],
        y=[driver2_pos[1]],
        mode='markers',
        marker=dict(size=12, color='#1E41FF', symbol='circle'),  # Red Bull Blue
        name='VER'
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False, fixedrange=True),  # fixedrange prevents zooming which breaks replay feel
        yaxis=dict(visible=False, fixedrange=True),
        showlegend=False
    )

    return fig