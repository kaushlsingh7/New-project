# 🦺 SafeStep AI

**Smart Safety Analysis for Walking Routes**

SafeStep AI is an intelligent Streamlit application that helps users assess walking route safety using real-time analysis of traffic conditions, crowd density, time of day, and distance. The app provides safety scores (0-10), ride-sharing options (Uber & Rapido), and women-specific safety features for night travel.

## 🎯 Features

- **Route Safety Scoring**: Intelligent scoring (0-10) based on:
  - Distance walked
  - Time of day (night = higher risk)
  - Traffic conditions
  - Crowd density estimates
  
- **Interactive Map**: Click twice to select source and destination
  
- **Real-time Analysis**:
  - Traffic intensity tracking
  - Crowd density assessment
  - Personalized safety recommendations
  
- **Transportation Options**:
  - Uber (Auto & Moto)
  - Rapido (Bike & Auto)
  - Real-time fare estimation with surge pricing
  
- **Women Safety Mode** (Night 6 PM - 6 AM):
  - Emergency contact sharing via WhatsApp
  - QR codes for live location sharing
  - Pre-travel safety checklist
  - Safety awareness tips

## 📋 Files

- [`app.py`](app.py) — Main Streamlit application
- [`requirements.txt`](requirements.txt) — Python dependencies
- [`style.css`](style.css) — CSS styling (static version)
- [`index.html`](index.html) — HTML static version
- [`.streamlit/config.toml`](.streamlit/config.toml) — Streamlit configuration

## 🚀 Quick Start (Local)

### 1. Clone the Repository
```bash
git clone https://github.com/kaushlsingh7/New-project.git
cd New-project
```

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 🌐 Deploy with Streamlit Cloud

### Step 1: Ensure GitHub Repository is Set Up
Your code is already on GitHub at: `https://github.com/kaushlsingh7/New-project`

### Step 2: Deploy on Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Click **"New app"** button
3. Select:
   - **Repository**: `New-project`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Click **Deploy!**

Your app will be live at: `https://<username>-new-project.streamlit.app`

**Note**: You need a Streamlit Cloud account (free). Sign in with your GitHub account.

## 📦 Alternative Deployment Options

### Render.com (Free Tier Available)
1. Fork the repository (if not already done)
2. Visit [render.com](https://render.com)
3. Create new "Web Service"
4. Connect your GitHub account and select this repo
5. Set Build Command: `pip install -r requirements.txt`
6. Set Start Command: `streamlit run app.py --server.port=10000`

### Railway.app
1. Visit [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Authorize GitHub and select this repository
5. Railway will auto-detect Streamlit and deploy

### Heroku (Note: Free tier discontinued, but still deployable)
```bash
# Install Heroku CLI, then:
heroku login
heroku create your-app-name
git push heroku main
```

## 🔧 Configuration

Edit `.streamlit/config.toml` to customize:
- Theme colors (primary, background, text)
- Server settings
- Logging levels

## 📚 Requirements

- Python 3.7+
- dependencies listed in `requirements.txt`:
  - streamlit >= 1.20
  - pandas >= 1.3
  - folium >= 0.12
  - streamlit-folium >= 0.10
  - qrcode[pil] >= 7.4

## 🎨 Modern UI Features

- Beautiful gradient backgrounds
- Smooth card animations
- Interactive tabs for analysis
- Color-coded safety indicators
- Responsive design
- Professional typography

## 📱 Features Breakdown

### Safety Analysis
- Multi-factor scoring algorithm
- Real-time traffic simulation
- Crowd density estimation
- Safety color coding (🟢 Safe, 🟡 Caution, 🔴 Danger)

### transportation Options
- Fare estimation for 4 ride types
- Dynamic surge pricing (1.0x - 1.3x)
- Duration estimates
- Safety ratings per vehicle type

### Women Safety
- Night mode auto-activation (6 PM - 6 AM)
- Emergency contact WhatsApp integration
- Live location QR code generation
- Comprehensive safety checklist
- Pre-travel, during, and post-arrival tips

## 🐛 Troubleshooting

**App won't start:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.7+)

**Map not loading:**
- Ensure internet connection
- Check that folium is properly installed

**QR code not generating:**
- Verify qrcode[pil] is installed: `pip install qrcode[pil]`

## 📈 Future Enhancements

- Real Google Maps API integration
- Historical crime data analysis
- User reviews and ratings
- Machine learning route optimization
- Multi-language support
- Mobile app version

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

## 👨‍💻 Author

**Kaushlendra Singh**
- GitHub: [@kaushlsingh7](https://github.com/kaushlsingh7)
- Email: kaushlsingh7@gmail.com

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Built with ❤️ using Streamlit**

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

