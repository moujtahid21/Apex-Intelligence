# 🏎️ Apex Intelligence: F1 Telemetry & AI Dashboard

**Apex Intelligence** is a comprehensive Formula 1 telemetry analysis tool built with **Python** and **Streamlit**. It leverages the [FastF1](https://github.com/theOehrly/Fast-F1) library to visualize real-time race data, compare driver performance, simulate AI-driven lap predictions, and export data for sim racing (Assetto Corsa/MoTeC).

## ✨ Key Features

### 🏁 1. Event Overview

* **Live Dashboard:** View track temperature, air temperature, and humidity for any selected session.
* **Fastest Lap Card:** Automatically displays the fastest driver with a smart-cropped portrait and lap time.
* **Enhanced Track Map:** accurate circuit geometry with turn numbers labeled.

### 📈 2. Telemetry Analysis

* **Driver vs. Driver:** Compare speed, throttle, brake, RPM, and gear traces between any two drivers.
* **Channel Selector:** Switch between different telemetry channels to analyze specific driving inputs.
* **Zoom & Pan:** Interactive Matplotlib charts for deep-dive analysis.

### 🧠 3. AI Performance Predictor (Simulation)

* **Lap Time Oracle:** Simulates lap times based on variable conditions (fuel load, track temp, tyre compound).
* **Explainability:** Visualizes "Feature Importance" (SHAP-like values) to show why a predicted time is faster or slower.
* **Neural Network Viz:** Displays the architecture of the simulation model.

### 🏎️ 4. Strategy & Stints

* **Tyre History:** Visualizes every stint for the top 10 drivers.
* **Compound Legend:** Custom-built HTML component displaying official Pirelli tire colors and assets.
* **Strategy Guide:** Interactive pop-up card explaining the characteristics of Soft, Medium, and Hard compounds.

### 🎮 5. Sim Racing Export (MoTeC)

* **Assetto Corsa Ready:** Exports real F1 telemetry into MoTeC i2 Pro compatible CSV files.
* **Auto-Correction:** Automatically finds the fastest lap for a selected driver to ensure the best reference data.

---

## 🛠️ Installation & Setup

### Prerequisites

* Python 3.10 or higher
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/apex-intelligence.git
cd apex-intelligence

```

### 2. Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

### 4. Asset Setup

Ensure you have the following folder structure for images (images are not included in the repo due to copyright, you must add your own):

```text
assets/
├── drivers/           # Driver portraits (e.g., VER.png, HAM.png)
└── tires/             # Pirelli tire SVGs (e.g., F1_tire_Pirelli_PZero_Red_18.svg)

```

---

## 🚀 Usage

Run the Streamlit app locally:

```bash
streamlit run app.py

```

1. **Select Year & Grand Prix:** Use the sidebar to choose the season and specific race event.
2. **Load Data:** Click "Load Session Data". The first load may take a few seconds as FastF1 caches the data.
3. **Navigate Tabs:** Switch between Overview, Telemetry, AI, Strategy, and Export tabs to explore the data.

---

## 📂 Project Structure

```text
apex-intelligence/
├── app.py                   # Main application entry point
├── components/              # Modular UI components
│   ├── event_overview.py    # Tab 1: Track map & stats
│   ├── telemetry_view.py    # Tab 2: Telemetry plotting
│   ├── ai_predictor.py      # Tab 3: AI Simulation logic
│   ├── strategy_view.py     # Tab 4: Stint charts
│   ├── motec_view.py        # Tab 5: Export logic
│   ├── tyre_legend.py       # Custom HTML Component
│   └── html_component.py    # Base class for HTML
├── assets/                  # Images & Icons
├── cache/                   # FastF1 cache (auto-generated)
└── requirements.txt         # Python dependencies

```

---

## 🤝 Credits & Acknowledgements
If you want to use this project or contribute, please give credit to the original author.
``Author: Abdelbasset Moujtahid
Source: https://github.com/moujtahid21/Apex-Intelligence``

* **Data Source:** [FastF1 Library](https://github.com/theOehrly/Fast-F1) (uses F1 live timing data).
* **Visualization:** Matplotlib & Seaborn.
* **UI Framework:** Streamlit.

*Note: This project is unofficial and not associated in any way with the Formula 1 companies. F1, FORMULA ONE, FORMULA 1, FIA FORMULA ONE WORLD CHAMPIONSHIP, GRAND PRIX and related marks are trade marks of Formula One Licensing B.V.*