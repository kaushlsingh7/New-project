import math
import random
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import qrcode
from io import BytesIO


def haversine(lat1, lon1, lat2, lon2):
    """Return distance in kilometers between two lat/lon pairs."""
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def calculate_route_safety_score(src_lat, src_lon, dst_lat, dst_lon):
    """Calculate safety score (0-10) for a walking route based on:
    - Distance (longer = slightly riskier)
    - Time of day (night = riskier)
    - Traffic conditions (high traffic = more pollution, less safe)
    - Crowd density simulation
    
    Returns: safety_score (0-10), analysis_data (dict)
    """
    # Calculate distance
    distance_km = haversine(src_lat, src_lon, dst_lat, dst_lon)
    
    # Get current hour
    current_hour = datetime.now().hour
    is_night = current_hour < 6 or current_hour > 18
    
    # Base score starts at 8
    safety_score = 8.0
    
    # Deduct for distance (longer walks = more risk)
    # Every 2km adds risk
    if distance_km > 2:
        safety_score -= min((distance_km - 2) * 0.5, 2)  # Max -2 points
    
    # Deduct for time of day
    if is_night:
        safety_score -= 2.5  # Night time is significantly riskier
    elif 6 <= current_hour < 9 or 17 <= current_hour < 18:
        safety_score -= 1  # Rush hours a bit riskier
    
    # Simulate traffic conditions (in real implementation, use Google Maps Directions API)
    traffic_factor = random.uniform(0, 1)
    if traffic_factor > 0.7:  # Simulate high traffic (30% chance)
        safety_score -= 1.5  # High traffic = more pollution, less safe
    elif traffic_factor > 0.4:  # Medium traffic
        safety_score -= 0.5
    
    # Simulate crowd density based on time and location
    crowd_factor = random.uniform(0, 1)
    if is_night and crowd_factor > 0.5:
        safety_score -= 1  # Low crowd at night is risky
    elif not is_night and current_hour in [12, 13, 18, 19] and crowd_factor > 0.6:
        safety_score += 0.5  # Higher crowd during peak hours can be safer
    
    # Ensure score is between 1 and 10
    safety_score = max(1, min(10, safety_score))
    
    # Traffic level classification
    if traffic_factor > 0.7:
        traffic_level = "🔴 High Traffic"
    elif traffic_factor > 0.4:
        traffic_level = "🟡 Moderate Traffic"
    else:
        traffic_level = "🟢 Low Traffic"
    
    # Crowd level classification
    if is_night:
        crowd_level = "🔴 Low Crowd (Risky)"
    elif current_hour in [12, 13, 18, 19]:
        crowd_level = "🟢 High Crowd (Safer)"
    else:
        crowd_level = "🟡 Moderate Crowd"
    
    analysis_data = {
        "distance_km": distance_km,
        "time_of_day": f"{current_hour:02d}:00",
        "is_night": is_night,
        "traffic_level": traffic_level,
        "crowd_level": crowd_level,
        "traffic_factor": traffic_factor,
        "crowd_factor": crowd_factor
    }
    
    return round(safety_score, 2), analysis_data


def safety_color(score):
    """Return color based on safety score."""
    if score > 7:
        return "green"
    if score >= 5:
        return "orange"
    return "red"


def generate_location_qr(lat, lon, name):
    """Generate a QR code for sharing location via Google Maps link."""
    try:
        google_maps_link = f"https://maps.google.com/?q={lat},{lon}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(google_maps_link)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf, google_maps_link
    except Exception as e:
        return None, None


def calculate_ride_fares(distance_km):
    """Estimate fares for Uber and Rapido based on distance.
    
    Uses typical pricing models from Indian ride-sharing services.
    Note: These are estimates; actual prices may vary based on surge pricing, traffic, etc.
    """
    
    # Ensure minimum distance
    distance_km = max(distance_km, 0.5)
    
    # --- UBER PRICING (Estimated) ---
    # Uber Auto: ~₹8-10 base + ₹8-12 per km
    uber_auto_base = 40
    uber_auto_per_km = 10
    uber_auto_fare = uber_auto_base + (distance_km * uber_auto_per_km)
    uber_auto_min = min(uber_auto_fare, 150)  # Minimum fare
    
    # Uber Moto: ~₹5-8 base + ₹6-8 per km (cheaper, more risky)
    uber_moto_base = 20
    uber_moto_per_km = 7
    uber_moto_fare = uber_moto_base + (distance_km * uber_moto_per_km)
    uber_moto_min = min(uber_moto_fare, 100)
    
    # --- RAPIDO PRICING (Estimated) ---
    # Rapido Bike: Similar to Uber Moto
    rapido_bike_base = 15
    rapido_bike_per_km = 6
    rapido_bike_fare = rapido_bike_base + (distance_km * rapido_bike_per_km)
    rapido_bike_min = min(rapido_bike_fare, 80)
    
    # Rapido Auto/Cab: Similar to Uber Auto
    rapido_auto_base = 35
    rapido_auto_per_km = 9
    rapido_auto_fare = rapido_auto_base + (distance_km * rapido_auto_per_km)
    rapido_auto_min = min(rapido_auto_fare, 130)
    
    # Add surge pricing variability (~10-30% increase during peak hours)
    surge_multiplier = random.uniform(1.0, 1.3)
    
    fares = {
        "distance_km": distance_km,
        "uber": {
            "auto": {
                "name": "Uber Auto",
                "estimated_fare": round(uber_auto_min * surge_multiplier),
                "base": uber_auto_base,
                "per_km": uber_auto_per_km,
                "emoji": "🚗",
                "duration_min": int(distance_km * 3),  # ~3 min per km
                "safety": "Medium"
            },
            "moto": {
                "name": "Uber Moto",
                "estimated_fare": round(uber_moto_min * surge_multiplier),
                "base": uber_moto_base,
                "per_km": uber_moto_per_km,
                "emoji": "🏍️",
                "duration_min": int(distance_km * 2),  # ~2 min per km
                "safety": "Low (Bike)"
            }
        },
        "rapido": {
            "bike": {
                "name": "Rapido Bike",
                "estimated_fare": round(rapido_bike_min * surge_multiplier),
                "base": rapido_bike_base,
                "per_km": rapido_bike_per_km,
                "emoji": "🏍️",
                "duration_min": int(distance_km * 2),
                "safety": "Low (Bike)"
            },
            "auto": {
                "name": "Rapido Auto",
                "estimated_fare": round(rapido_auto_min * surge_multiplier),
                "base": rapido_auto_base,
                "per_km": rapido_auto_per_km,
                "emoji": "🚗",
                "duration_min": int(distance_km * 3),
                "safety": "Medium"
            }
        },
        "surge_multiplier": round(surge_multiplier, 2)
    }
    
    return fares


def main():
    st.set_page_config(page_title="SafeStep AI", layout="wide")

    # Modern Custom CSS with Beautiful Gradients and UI
    st.markdown("""
    <style>
    /* Modern Background */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* Page Container Background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #ffffff 0%, #f0f4f8 50%, #e8f0f7 100%);
    }
    
    /* Typography */
    h1, h2, h3 {
        color: #1a365d;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Modern Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    
    /* Card Styles */
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    .success-card {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 18px;
        border-radius: 12px;
        color: white;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #FF9800 0%, #e68a00 100%);
        padding: 18px;
        border-radius: 12px;
        color: white;
        border-left: 4px solid #FF9800;
        box-shadow: 0 4px 15px rgba(255, 152, 0, 0.2);
    }
    
    .danger-card {
        background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
        padding: 18px;
        border-radius: 12px;
        color: white;
        border-left: 4px solid #f44336;
        box-shadow: 0 4px 15px rgba(244, 67, 54, 0.2);
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1em;
        font-weight: 600;
        color: #1a365d;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 2px solid #e0e7f1;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        border-radius: 8px 8px 0 0;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Modern Buttons */
    .stButton > button {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Expander Styling */
    .stExpander {
        border: 1px solid #e0e7f1;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.8);
    }
    
    .stExpander > div:first-child {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.02) 100%);
        border-radius: 10px;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #e0e7f1;
        padding: 10px 12px;
        font-size: 1rem;
    }
    
    /* Checkbox Styling */
    .stCheckbox > label {
        font-weight: 500;
        color: #1a365d;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
    }
    
    /* Separator */
    hr {
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e0e7f1, transparent);
        margin: 2rem 0;
    }
    
    /* Divider with style */
    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # ===== HEADER SECTION =====
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.markdown('<h1 style="color: #1a365d; margin-bottom: 0;">🦺 SafeStep AI</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color: #4a5568; font-size: 1.05rem; margin-top: -1rem;">Smart Safety Analysis for Walking Routes</p>', unsafe_allow_html=True)
    
    with col_header2:
        st.markdown(f'''
        <div class="info-card" style="text-align: center;">
            <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 5px;">Current Time</div>
            <div style="font-size: 1.4rem; font-weight: 700;">{datetime.now().strftime('%H:%M')}</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown("---")

    # Initialize session state for map selections
    if "selected_source" not in st.session_state:
        st.session_state.selected_source = None
    if "selected_destination" not in st.session_state:
        st.session_state.selected_destination = None
    if "selection_step" not in st.session_state:
        st.session_state.selection_step = 1

    # ===== STEP 1: ROUTE SELECTION =====
    with st.container():
        st.markdown('<h2 style="color: #1a365d;">📍 Step 1: Select Your Route</h2>', unsafe_allow_html=True)
        
        # Instructions
        if st.session_state.selection_step == 1:
            st.markdown('''
            <div class="info-card">
                <strong>👆 Click on the map to select SOURCE location</strong>
                <p style="margin-bottom: 0;">Where are you starting from?</p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="success-card">
                <strong>✅ Source selected!</strong>
                <p style="margin-bottom: 0;">Now click to select your DESTINATION</p>
            </div>
            ''', unsafe_allow_html=True)
        
        # Create unified map
        unified_map = folium.Map(
            location=[26.8467, 80.9462],
            zoom_start=14,
            tiles="OpenStreetMap"
        )
        
        # Add markers if both locations are selected
        if st.session_state.selected_source:
            folium.Marker(
                location=[st.session_state.selected_source[0], st.session_state.selected_source[1]],
                popup="🔵 Source Location",
                icon=folium.Icon(color="blue", icon="play", prefix="fa")
            ).add_to(unified_map)
        
        if st.session_state.selected_destination:
            folium.Marker(
                location=[st.session_state.selected_destination[0], st.session_state.selected_destination[1]],
                popup="🟣 Destination Location",
                icon=folium.Icon(color="purple", icon="flag", prefix="fa")
            ).add_to(unified_map)
            
            # Add polyline connecting source and destination
            if st.session_state.selected_source:
                folium.PolyLine(
                    locations=[
                        [st.session_state.selected_source[0], st.session_state.selected_source[1]],
                        [st.session_state.selected_destination[0], st.session_state.selected_destination[1]]
                    ],
                    color="blue",
                    weight=2,
                    opacity=0.7,
                    dash_array="5, 5"
                ).add_to(unified_map)
        
        # Display the map
        map_data = st_folium(unified_map, width=1400, height=500, key="unified_map")
        
        # Handle map clicks
        if map_data and map_data.get("last_clicked"):
            if st.session_state.selection_step == 1:
                st.session_state.selected_source = (
                    map_data["last_clicked"]["lat"],
                    map_data["last_clicked"]["lng"]
                )
                st.session_state.selection_step = 2
                st.rerun()
            elif st.session_state.selection_step == 2:
                st.session_state.selected_destination = (
                    map_data["last_clicked"]["lat"],
                    map_data["last_clicked"]["lng"]
                )
                st.rerun()
        
        # Display selected locations in nice format
        st.markdown("")
        loc_col1, loc_col2, loc_col3 = st.columns([2, 2, 1])
        
        with loc_col1:
            if st.session_state.selected_source:
                st.markdown(f'''
                <div class="success-card">
                    <strong>✅ Source Selected</strong><br>
                    <code style="color: #f0f4f8; font-size: 0.9rem;">{st.session_state.selected_source[0]:.6f}, {st.session_state.selected_source[1]:.6f}</code>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown('''
                <div class="warning-card">
                    <strong>⏳ SOURCE</strong><br>
                    <span style="font-size: 0.9rem;">Waiting for selection...</span>
                </div>
                ''', unsafe_allow_html=True)
        
        with loc_col2:
            if st.session_state.selected_destination:
                st.markdown(f'''
                <div class="success-card">
                    <strong>✅ Destination Selected</strong><br>
                    <code style="color: #f0f4f8; font-size: 0.9rem;">{st.session_state.selected_destination[0]:.6f}, {st.session_state.selected_destination[1]:.6f}</code>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown('''
                <div class="warning-card">
                    <strong>⏳ DESTINATION</strong><br>
                    <span style="font-size: 0.9rem;">Waiting for selection...</span>
                </div>
                ''', unsafe_allow_html=True)
        
        with loc_col3:
            if st.session_state.selected_source or st.session_state.selected_destination:
                if st.button("🔄 Clear", use_container_width=True):
                    st.session_state.selected_source = None
                    st.session_state.selected_destination = None
                    st.session_state.selection_step = 1
                    st.rerun()

    # ===== STEP 2: SAFETY ANALYSIS =====
    if st.session_state.selected_source and st.session_state.selected_destination:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #1a365d;">📊 Step 2: Safety Analysis & Recommendations</h2>', unsafe_allow_html=True)
        
        src_lat, src_lon = st.session_state.selected_source
        dst_lat, dst_lon = st.session_state.selected_destination
        
        # Calculate safety score
        safety_score, analysis_data = calculate_route_safety_score(src_lat, src_lon, dst_lat, dst_lon)
        
        # ===== ROUTE OVERVIEW CARDS =====
        st.markdown('<h3 style="color: #1a365d;">📈 Route Overview</h3>', unsafe_allow_html=True)
        overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
        
        with overview_col1:
            st.metric("📏 Distance", f"{analysis_data['distance_km']:.2f} km")
        
        with overview_col2:
            st.metric("🕐 Time", analysis_data['time_of_day'])
        
        with overview_col3:
            color = safety_color(safety_score)
            if color == "green":
                st.success(f"✅ Score: {safety_score}/10")
            elif color == "orange":
                st.warning(f"⚠️ Score: {safety_score}/10")
            else:
                st.error(f"⛔ Score: {safety_score}/10")
        
        with overview_col4:
            if analysis_data['is_night']:
                st.error("🌙 Night Travel")
            else:
                st.success("☀️ Daytime")
        
        # ===== DETAILED ANALYSIS TABS =====
        st.markdown("")
        tab1, tab2, tab3, tab4 = st.tabs(["🚦 Traffic", "👥 Crowd", "📋 Recommendations", "💡 Tips"])
        
        with tab1:
            col_traffic1, col_traffic2 = st.columns(2)
            with col_traffic1:
                st.markdown("### Traffic Conditions")
                st.markdown(f"**Status:** {analysis_data['traffic_level']}")
                st.progress(analysis_data['traffic_factor'], text=f"Intensity: {analysis_data['traffic_factor']*100:.1f}%")
                
                if analysis_data['traffic_factor'] > 0.7:
                    st.warning("🚗 Heavy traffic detected! Air pollution & congestion risk")
                elif analysis_data['traffic_factor'] > 0.4:
                    st.info("⚠️ Moderate traffic conditions")
                else:
                    st.success("✅ Light traffic - Good visibility")
            
            with col_traffic2:
                st.markdown("### What it Means")
                st.markdown("""
                **High Traffic (>70%):**
                - More pollution exposure
                - Less visibility for pedestrians
                - Vehicle emissions

                **Moderate Traffic (40-70%):**
                - Normal city conditions
                - Manageable pedestrian space

                **Light Traffic (<40%):**
                - Clear roads
                - Good pedestrian safety
                - Better air quality
                """)
        
        with tab2:
            col_crowd1, col_crowd2 = st.columns(2)
            with col_crowd1:
                st.markdown("### Crowd Density")
                st.markdown(f"**Status:** {analysis_data['crowd_level']}")
                
                if analysis_data['is_night']:
                    st.error("🔴 Low Crowd at Night - High Risk")
                    st.warning("Fewer witnesses available in case of emergency")
                elif "High" in analysis_data['crowd_level']:
                    st.success("🟢 High Crowd - Safer Environment")
                    st.info("More people around means better visibility & help availability")
                else:
                    st.warning("🟡 Moderate Crowd - Average Safety")
            
            with col_crowd2:
                st.markdown("### Safety Implications")
                st.markdown("""
                **High Crowd (Safe):**
                - More witnesses
                - Easier to get help
                - Better visibility
                - Strength in numbers

                **Low Crowd (Risky):**
                - Fewer witnesses
                - Harder to find help
                - Less visibility
                - Potential isolation
                """)
        
        with tab3:
            st.markdown("### 🛡️ Safety Recommendations")
            
            if safety_score > 7:
                st.success("### ✅ Safe Route")
                st.markdown("""
                This route appears **relatively safe**. Follow standard safety practices:
                - Stay alert and aware of surroundings
                - Keep your phone charged
                - Follow traffic rules
                - Avoid distractions while walking
                """)
            elif safety_score >= 5:
                st.warning("### ⚠️ Moderate Caution Needed")
                st.markdown("""
                **Recommended Actions:**
                - Walk in groups when possible
                - Avoid isolated side streets
                - Stick to well-lit main roads
                - Keep your phone charged and ready
                - Share your location with someone trusted
                - Trust your instincts
                """)
            else:
                st.error("### ⛔ High Risk - Consider Alternatives")
                st.markdown("""
                **Strongly Recommended Actions:**
                - Consider postponing to daytime
                - Use alternative routes through busier areas
                - Arrange transportation (taxi, ride-share, friend)
                - Go with trusted companions
                - Report any safety hazards to local authorities
                - Stay in well-populated areas
                """)
        
        with tab4:
            st.markdown("### 💡 Additional Tips")
            col_tips1, col_tips2 = st.columns(2)
            
            with col_tips1:
                st.markdown("**General Safety Tips:**")
                st.markdown("""
                ✓ Wear bright/visible clothing
                ✓ Keep emergency numbers accessible
                ✓ Don't use headphones at max volume
                ✓ Trust your gut feeling
                ✓ Keep valuables secure and hidden
                ✓ Walk confidently
                ✓ Stay on main roads
                """)
            
            with col_tips2:
                st.markdown("**Digital Safety:**")
                st.markdown("""
                ✓ Share live location with contacts
                ✓ Keep phone battery above 20%
                ✓ Have emergency contacts saved
                ✓ Screenshot route on phone
                ✓ Avoid sharing real-time posts
                ✓ Enable location services
                ✓ Use ride-sharing with shared ride
                """)
        
        # ===== RIDE OPTIONS SECTION =====
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #1a365d;">🚗 Step 3: Transportation Options</h2>', unsafe_allow_html=True)
        
        fares = calculate_ride_fares(analysis_data['distance_km'])
        
        ride_tab1, ride_tab2 = st.tabs(["🚕 UBER", "🏍️ RAPIDO"])
        
        with ride_tab1:
            uber_col1, uber_col2 = st.columns(2)
            
            with uber_col1:
                st.markdown(f'''
                <div style="background: linear-gradient(135deg, rgba(0, 0, 0, 0.05) 0%, rgba(102, 126, 234, 0.05) 100%); padding: 20px; border-radius: 12px; border: 1px solid #e0e7f1;">
                    <h3 style="color: #1a365d; margin-top: 0;">{fares['uber']['auto']['emoji']} Uber Auto</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 15px 0;">
                        <div style="text-align: center; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.8rem; color: #666;">Fare</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">₹{fares['uber']['auto']['estimated_fare']}</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.8rem; color: #666;">Time</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">~{fares['uber']['auto']['duration_min']}m</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.8rem; color: #666;">Safety</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">{fares['uber']['auto']['safety']}</div>
                        </div>
                    </div>
                    <p style="font-size: 0.9rem; color: #666; margin: 10px 0;">₹{fares['uber']['auto']['base']} + ₹{fares['uber']['auto']['per_km']}/km</p>
                </div>
                ''', unsafe_allow_html=True)
                if st.button("📱 Book Uber Auto", key="uber_auto", use_container_width=True):
                    st.success("🚗 Opening Uber app...")
            
            with uber_col2:
                st.markdown(f'''
                <div style="background: linear-gradient(135deg, rgba(0, 0, 0, 0.05) 0%, rgba(102, 126, 234, 0.05) 100%); padding: 20px; border-radius: 12px; border: 1px solid #e0e7f1;">
                    <h3 style="color: #1a365d; margin-top: 0;">{fares['uber']['moto']['emoji']} Uber Moto</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 15px 0;">
                        <div style="text-align: center; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.8rem; color: #666;">Fare</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">₹{fares['uber']['moto']['estimated_fare']}</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.8rem; color: #666;">Time</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">~{fares['uber']['moto']['duration_min']}m</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.8rem; color: #666;">Safety</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">{fares['uber']['moto']['safety']}</div>
                        </div>
                    </div>
                    <p style="font-size: 0.9rem; color: #666; margin: 10px 0;">₹{fares['uber']['moto']['base']} + ₹{fares['uber']['moto']['per_km']}/km</p>
                </div>
                ''', unsafe_allow_html=True)
                if st.button("📱 Book Uber Moto", key="uber_moto", use_container_width=True):
                    st.success("🚗 Opening Uber app...")
        
        with ride_tab2:
            rapido_col1, rapido_col2 = st.columns(2)
            
            with rapido_col1:
                st.markdown(f'''
                <div style="background: linear-gradient(135deg, rgba(0, 0, 0, 0.05) 0%, rgba(102, 126, 234, 0.05) 100%); padding: 20px; border-radius: 12px; border: 1px solid #e0e7f1;">
                    <h3 style="color: #1a365d; margin-top: 0;">{fares['rapido']['bike']['emoji']} Rapido Bike</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 15px 0;">
                        <div style="text-align: center; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.8rem; color: #666;">Fare</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">₹{fares['rapido']['bike']['estimated_fare']}</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.8rem; color: #666;">Time</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">~{fares['rapido']['bike']['duration_min']}m</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.8rem; color: #666;">Safety</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">{fares['rapido']['bike']['safety']}</div>
                        </div>
                    </div>
                    <p style="font-size: 0.9rem; color: #666; margin: 10px 0;">₹{fares['rapido']['bike']['base']} + ₹{fares['rapido']['bike']['per_km']}/km</p>
                </div>
                ''', unsafe_allow_html=True)
                if st.button("📱 Book Rapido Bike", key="rapido_bike", use_container_width=True):
                    st.success("🏍️ Opening Rapido app...")
            
            with rapido_col2:
                st.markdown(f'''
                <div style="background: linear-gradient(135deg, rgba(0, 0, 0, 0.05) 0%, rgba(102, 126, 234, 0.05) 100%); padding: 20px; border-radius: 12px; border: 1px solid #e0e7f1;">
                    <h3 style="color: #1a365d; margin-top: 0;">{fares['rapido']['auto']['emoji']} Rapido Auto</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 15px 0;">
                        <div style="text-align: center; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.8rem; color: #666;">Fare</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">₹{fares['rapido']['auto']['estimated_fare']}</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.8rem; color: #666;">Time</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">~{fares['rapido']['auto']['duration_min']}m</div>
                        </div>
                        <div style="text-align: center; padding: 10px; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
                            <div style="font-size: 0.8rem; color: #666;">Safety</div>
                            <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">{fares['rapido']['auto']['safety']}</div>
                        </div>
                    </div>
                    <p style="font-size: 0.9rem; color: #666; margin: 10px 0;">₹{fares['rapido']['auto']['base']} + ₹{fares['rapido']['auto']['per_km']}/km</p>
                </div>
                ''', unsafe_allow_html=True)
                if st.button("📱 Book Rapido Auto", key="rapido_auto", use_container_width=True):
                    st.success("🏍️ Opening Rapido app...")
        
        st.markdown('''
        <div class="info-card">
            <strong>💡 Surge Multiplier: {0}x</strong>
            <p style="margin-bottom: 0;">May vary during peak hours</p>
        </div>
        '''.format(fares['surge_multiplier']), unsafe_allow_html=True)
        st.caption("⚠️ Prices are estimates. Actual prices may vary due to surge pricing, traffic, and availability.")
        
        # ===== WOMEN SAFETY SECTION =====
        current_hour = datetime.now().hour
        is_night = current_hour < 6 or current_hour > 18
        
        if is_night:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown('<h2 style="color: #1a365d;">👩‍🦰 Step 4: Women Safety - Night Mode</h2>', unsafe_allow_html=True)
            
            with st.container():
                safety_col1, safety_col2, safety_col3 = st.columns(3)
                
                # Emergency Contact
                with safety_col1:
                    st.subheader("📞 Emergency Contact")
                    emergency_name = st.text_input("Contact Name", placeholder="Mom, Sister, Friend", key="emerg_name")
                    emergency_phone = st.text_input("Phone Number", placeholder="10-digit mobile", key="emerg_phone", max_chars=10)
                    
                    if emergency_name and emergency_phone and len(emergency_phone) == 10:
                        if st.button("💬 Share via WhatsApp", key="send_whatsapp", use_container_width=True):
                            msg = f"🆘 I'm traveling now.\n\n📍 From: {src_lat:.6f}, {src_lon:.6f}\n📍 To: {dst_lat:.6f}, {dst_lon:.6f}\n\n📏 Distance: {analysis_data['distance_km']:.2f} km\n⚖️ Safety: {safety_score}/10"
                            whatsapp_link = f"https://wa.me/91{emergency_phone}?text={msg.replace(chr(10), '%0A').replace(' ', '%20')}"
                            st.success("✅ Ready to share!")
                            st.code(whatsapp_link, language="text")
                
                # QR Code for Current Location
                with safety_col2:
                    st.subheader("📍 Share Current Location")
                    qr_img, maps_link = generate_location_qr(src_lat, src_lon, "Current Location")
                    
                    if qr_img:
                        st.image(qr_img, caption="Scan to see location", use_column_width=True)
                        st.caption(f"📌 {src_lat:.4f}, {src_lon:.4f}")
                        if st.button("🔗 Copy Link", key="copy_location", use_container_width=True):
                            st.success(f"✅ {maps_link}")
                
                # Destination QR
                with safety_col3:
                    st.subheader("📍 Destination QR Code")
                    qr_img_dst, maps_link_dst = generate_location_qr(dst_lat, dst_lon, "Destination")
                    
                    if qr_img_dst:
                        st.image(qr_img_dst, caption="Share destination", use_column_width=True)
                        st.caption(f"📌 {dst_lat:.4f}, {dst_lon:.4f}")
                        if st.button("📋 Copy Destination", key="copy_destination", use_container_width=True):
                            st.success(f"✅ {maps_link_dst}")
            
            # Safety Checklist
            st.markdown("")
            with st.expander("✅ Pre-Travel Safety Checklist", expanded=True):
                check_col1, check_col2, check_col3 = st.columns(3)
                
                with check_col1:
                    st.markdown("**Before Leaving:**")
                    st.checkbox("📱 Phone charged to 100%", value=True)
                    st.checkbox("👤 Informed trusted contact", value=False)
                    st.checkbox("📞 Emergency contacts saved", value=False)
                    st.checkbox("👕 Wore bright clothing", value=False)
                
                with check_col2:
                    st.markdown("**During Travel:**")
                    st.checkbox("🛣️ On main, lit roads", value=False)
                    st.checkbox("👀 Aware of surroundings", value=False)
                    st.checkbox("📍 Sharing live location", value=False)
                    st.checkbox("🚫 Avoiding strangers", value=False)
                
                with check_col3:
                    st.markdown("**After Arrival:**")
                    st.checkbox("✅ Confirmed safe arrival", value=False)
                    st.checkbox("📸 Documented journey", value=False)
                    st.checkbox("⏰ Logged arrival time", value=False)
                    st.checkbox("🚨 Reported any issues", value=False)
        
        # Recalculate button
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        if st.button("🔄 Recalculate Route", use_container_width=True):
            st.rerun()
    
    else:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('''
        <div class="info-card" style="text-align: center;">
            <strong>👈 Select both source and destination on the map above to begin</strong>
            <p style="margin-bottom: 0;">Click twice on the map to start your safety analysis</p>
        </div>
        ''', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
