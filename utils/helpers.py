import numpy as np
from PIL import Image
import os
import base64


def crop_to_face(image_path):
    """
    Crops the top 20% of a tall portrait image to focus on the face.
    """
    try:
        img = Image.open(image_path)
        width, height = img.size
        target_height = int(width * 0.85)
        img_cropped = img.crop((0, 0, width, target_height))
        return img_cropped
    except Exception:
        return None


def get_img_as_base64(file_path):
    """
    Converts an image file to base64 string for HTML embedding.
    """
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def calculate_tyre_health(session, lap):
    """
    Calculates tyre degradation and estimated health percentage.
    """
    try:
        driver = lap['Driver']
        stint_id = lap['Stint']

        # Get all laps for this driver
        laps = session.laps.pick_driver(driver)

        # Filter for the specific stint and accurate racing laps
        stint_laps = laps[laps['Stint'] == stint_id]
        stint_laps = stint_laps.pick_quicklaps().pick_accurate()

        if len(stint_laps) < 3:
            return "N/A", "N/A"

        # Linear Regression: LapNumber vs LapTime (seconds)
        x = stint_laps['LapNumber'].values
        y = stint_laps['LapTime'].dt.total_seconds().values

        slope, intercept = np.polyfit(x, y, 1)

        if slope <= 0:
            health_pct = 100
            deg_str = "Improving"
        else:
            max_allowed_drop = 2.0  # seconds
            estimated_total_life = max_allowed_drop / slope
            laps_driven = lap['LapNumber'] - stint_laps['LapNumber'].min()

            health_pct = max(0, 100 * (1 - (laps_driven / estimated_total_life)))
            deg_str = f"+{slope:.3f}s/lap"

        return int(health_pct), deg_str

    except Exception:
        return "N/A", "N/A"


def calculate_driver_rating(session, driver_code):
    """
    Calculates a 0-10 rating based on the driver's theoretical best lap
    (sum of the best sectors) vs their actual best lap.
    """
    try:
        # Get all valid laps for the driver
        laps = session.laps.pick_driver(driver_code).pick_quicklaps().pick_accurate()

        if laps.empty:
            return "N/A"

        # 1. Actual Best Lap
        actual_best = laps.pick_fastest()['LapTime'].total_seconds()

        # 2. Theoretical Best Lap (Sum of Best Sectors)
        best_s1 = laps['Sector1Time'].min().total_seconds()
        best_s2 = laps['Sector2Time'].min().total_seconds()
        best_s3 = laps['Sector3Time'].min().total_seconds()

        theoretical_best = best_s1 + best_s2 + best_s3

        # 3. Calculate Delta (Time left on track)
        delta = actual_best - theoretical_best

        # 4. Scoring: Start at 10. Lose 1 point for every 0.1s missed.
        # This rewards precision/racecraft.
        rating = 10.0 - (delta * 10)

        # Clamp between 1.0 and 10.0
        rating = max(1.0, min(10.0, rating))

        return round(rating, 1)

    except Exception:
        return "N/A"