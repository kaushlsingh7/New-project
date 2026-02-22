# SafeStep AI

A small Streamlit app to help users find safer walking routes using synthetic "Safety Scores" (lighting, crowd density, historical data).

Files
- [app.py](app.py) — main Streamlit application
- [requirements.txt](requirements.txt) — Python dependencies

Quick start (VS Code / Terminal)

1. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# or Command Prompt
.\.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

Notes
- The app uses synthetic data generated at runtime. Adjust `generate_mock_data()` in `app.py` to change city center or sample size.
- Open the workspace in VS Code, ensure the Python interpreter is set to your virtual environment, then run the Streamlit command in the integrated terminal.

Troubleshooting
- If the folium map does not display, ensure `streamlit-folium` is installed and you are running a compatible Streamlit version.

New features (UI improvements)
- Custom source/destination: pick from generated points or enter custom latitude/longitude.
- Distance filter: slider to control search radius for suggestions.
- Safety threshold: show only points with a minimum safety score.
- Map legend and a polyline between source and destination for clarity.
- Top suggestions panel with "Center map here" buttons and CSV download of the displayed dataset.
 - Quick jump: search a city name (common presets), a `Location Name` from the dataset, or enter `lat,lon` to rapidly center the map.

