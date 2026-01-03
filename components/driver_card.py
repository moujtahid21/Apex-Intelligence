import textwrap

import streamlit as st


def render_driver_card(lap_time, driver_name, team_name, rating):
    """
    Renders a styled AWS-like driver card.
    """
    if rating != "N/A":
        rating_val = float(rating)
        rating_width = min(100, max(0, rating_val * 10))
    else:
        rating_val = "N/A"
        rating_width = 0

    # HTML must start at the beginning of the line!
    html_code = f"""
<div style='text-align: center; margin-top: -10px;'>
    <div style='margin-bottom: 5px;'>
        <span style='font-size: 1.5rem; font-weight: 800; color: #ff1801; line-height: 1; letter-spacing: -1px;'>
            {lap_time}
        </span>
    </div>

    <div style='margin-bottom: 15px;'>
        <div style='font-size: 1.3rem; font-weight: 700; color: #fff;'>{driver_name}</div>
        <div style='font-size: 0.9rem; color: #888; text-transform: uppercase; letter-spacing: 1px;'>{team_name}</div>
    </div>

    <div style='text-align: left; background-color: #262730; padding: 12px; border-radius: 8px; border: 1px solid #333;'>
        <div style='display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 6px;'>
            <span style='font-size: 0.7rem; font-weight: 700; color: #aaa; letter-spacing: 1px;'>PERFORMANCE RATING</span>
            <span style='font-size: 1.1rem; font-weight: 700; color: #fff;'>{rating_val}</span>
        </div>
        <div style='width: 100%; background-color: #444; height: 6px; border-radius: 3px; overflow: hidden;'>
            <div style='width: {rating_width}%; background-color: #ff1801; height: 100%; border-radius: 3px;'></div>
        </div>
    </div>
</div>
"""

    st.html(html_code)