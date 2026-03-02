# app.py — Run with: streamlit running app.py
import streamlit as st
import pickle
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from data_fetch import get_weather_risk

# Load model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Risk score calculator
def calculate_risk_score(rd, ts, price_change, crop_stage, soil_moisture, expenditure):
    score = 0
    if rd < -30: score += 35
    elif rd < -15: score += 20
    if ts > 6: score += 20
    elif ts > 3: score += 10
    if price_change < -20: score += 25
    elif price_change < -10: score += 15
    if crop_stage == 3: score += 10
    if soil_moisture < 3: score += 10
    if expenditure > 2: score += 10
    return min(score, 100)

# PAGE CONFIG
st.set_page_config(page_title="AgriSOS", page_icon="🌾", layout="wide")

st.markdown("""
<style>
    .main-title { font-size: 2.5rem; font-weight: 800; color: #2d6a4f; }
    .risk-high { background: #ff4444; color: white; padding: 15px; border-radius: 10px; text-align:center; font-size:1.5rem; font-weight:bold;}
    .risk-medium { background: #ff9800; color: white; padding: 15px; border-radius: 10px; text-align:center; font-size:1.5rem; font-weight:bold;}
    .risk-low { background: #4caf50; color: white; padding: 15px; border-radius: 10px; text-align:center; font-size:1.5rem; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #1b4332, #2d6a4f); padding: 2rem 2.5rem; border-radius: 16px; margin-bottom: 1.5rem;">
    <h1 style="color: white; font-size: 2.8rem; font-weight: 900; margin: 0;">🌾 AgriSOS</h1>
    <p style="color: #b7e4c7; font-size: 1.1rem; margin: 0.4rem 0 0;">Early Farmer Distress Prediction & Risk Advisory System </p>
</div>
""", unsafe_allow_html=True)

# TABS
tab1, tab2, tab3 = st.tabs(["🧑‍🌾 Farmer Risk Assessment", "📊 District Dashboard", "📈 Market Trends"])

# ── TAB 1: FARMER FORM ────────────────────────────────────────
with tab1:
    st.subheader("Enter Farmer Details")

    col1, col2 = st.columns(2)
    with col1:
        farmer_name = st.text_input("Farmer Name", "Ravi Kumar")
        crop = st.selectbox("Crop", ["Paddy", "Wheat", "Cotton", "Sugarcane", "Maize"])
        district = st.selectbox("District", ["Thanjavur", "Nagpur", "Ludhiana", "Warangal", "Nashik"])
        crop_stage = st.selectbox("Crop Growth Stage",
                                   [1, 2, 3, 4],
                                   format_func=lambda x: {1:"Sowing", 2:"Vegetative", 3:"Flowering (Critical)", 4:"Harvest"}[x])
    with col2:
        soil_type = st.selectbox("Soil Type", ["Black Cotton", "Red Loamy", "Alluvial", "Sandy Loam", "Clay"])
        soil_moisture = st.slider("Soil Moisture Level", 1, 10, 5, help="1=Very Dry, 10=Optimal")
        price_change = st.slider("Market Price Change (%)", -50, 20, -10,
                                  help="Estimated change in your crop's market price this season")
        expenditure_ratio = st.slider("Input Cost vs Normal", 0.5, 3.0, 1.2, step=0.1,
                                       help="1.0 = normal costs, 2.0 = double the usual costs")

    if st.button("Predict Distress Risk", type="primary", use_container_width=True):
        with st.spinner("Fetching real-time weather data..."):
            weather = get_weather_risk(district)
            rd = weather["rainfall_deviation"]
            ts = weather["temperature_stress"]

        features = np.array([[rd, ts, price_change, crop_stage, soil_moisture, expenditure_ratio]])
        prediction = model.predict(features)[0]
        proba = model.predict_proba(features)[0]
        risk_score = calculate_risk_score(rd, ts, price_change, crop_stage, soil_moisture, expenditure_ratio)

        st.divider()
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("🌧️ Rainfall Deviation", f"{rd:.1f}%", delta="vs normal")
        col_b.metric("🌡️ Temperature Stress", f"{ts:.1f}°C above optimal")
        col_c.metric("📊 Risk Score", f"{risk_score}/100")

        st.divider()
        risk_class = f'risk-{prediction.lower()}'
        risk_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}[prediction]
        st.markdown(
            f'<div class="{risk_class}">{risk_emoji} {farmer_name} — {prediction.upper()} DISTRESS RISK (Score: {risk_score}/100)</div>',
            unsafe_allow_html=True
        )

        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            title={'text': "Distress Risk Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#ff4444" if risk_score > 60 else "#ff9800" if risk_score > 35 else "#4caf50"},
                'steps': [
                    {'range': [0, 35],  'color': "#e8f5e9"},
                    {'range': [35, 60], 'color': "#fff3e0"},
                    {'range': [60, 100],'color': "#ffebee"}
                ]
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

        # Recommendations
        st.subheader("📋 Recommended Actions")
        recs = {
            "High": [
                "1. Apply for PM-Fasal Bima Yojana crop insurance immediately",
                "2. Install drip irrigation — rainfall deficit is critical",
                "3. Contact your local KVK (Krishi Vigyan Kendra) within 48 hours",
                "4. Defer non-essential input purchases to conserve cash",
                "5. Consider switching to drought-resistant varieties for next season"
            ],
            "Medium": [
                "1. Monitor soil moisture daily for the next 2 weeks",
                "2. Hold crop stock — market prices may recover in 10–15 days",
                "3. Check government MSP announcements for your crop",
                "4. Explore micro-irrigation subsidies in your district"
            ],
            "Low": [
                "1. Conditions are currently favorable — maintain current practices",
                "2. Plan next season inputs in advance to avoid price spikes",
                "3. Consider diversifying crops for risk distribution"
            ]
        }
        for rec in recs[prediction]:
            st.write(rec)

        # Feature importance bar
        feature_names = ['Rainfall', 'Temp Stress', 'Market Price', 'Crop Stage', 'Soil Moisture', 'Expenditure']
        importances = model.feature_importances_
        fig2 = px.bar(x=importances, y=feature_names, orientation='h',
              title="🔬 Risk Factor Contribution — Model Explanation",
              color=importances, color_continuous_scale='RdYlGn_r',
              labels={'x': 'Importance Score', 'y': 'Risk Factor'})
        fig2.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

# ── TAB 2: DISTRICT DASHBOARD ─────────────────────────────────
with tab2:
    st.subheader("District-Level Risk Overview")

    districts_data = pd.DataFrame({
        'District': ['Thanjavur', 'Nagpur', 'Ludhiana', 'Warangal', 'Nashik',
                     'Pune', 'Amravati', 'Jalgaon', 'Nanded', 'Solapur'],
        'Risk_Score': [72, 45, 28, 81, 55, 38, 68, 74, 61, 49],
        'Farmers_At_Risk': [1240, 890, 320, 1580, 670, 410, 1100, 1320, 950, 720],
        'Primary_Crop': ['Paddy','Cotton','Wheat','Cotton','Grapes','Sugarcane','Cotton','Banana','Cotton','Sugarcane']
    })

    districts_data['Risk_Level'] = districts_data['Risk_Score'].apply(
        lambda x: '🔴 High' if x > 60 else '🟡 Medium' if x > 35 else '🟢 Low'
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 High Risk Districts", len(districts_data[districts_data['Risk_Score'] > 60]))
    col2.metric("👨‍🌾 Total Farmers at Risk", f"{districts_data['Farmers_At_Risk'].sum():,}")
    col3.metric("📍 Districts Monitored", len(districts_data))

    fig3 = px.bar(districts_data.sort_values('Risk_Score', ascending=True),
                  x='Risk_Score', y='District', orientation='h',
                  color='Risk_Score', color_continuous_scale='RdYlGn_r',
                  title="District-wise Distress Risk Scores",
                  hover_data=['Farmers_At_Risk', 'Primary_Crop'])
    st.plotly_chart(fig3, use_container_width=True)

    st.dataframe(districts_data[['District','Primary_Crop','Risk_Score','Risk_Level','Farmers_At_Risk']],
                 use_container_width=True)

# ── TAB 3: MARKET TRENDS ──────────────────────────────────────
with tab3:
    st.subheader("📈 Crop Market Price Trends")

    np.random.seed(42)
    days = pd.date_range(end=pd.Timestamp.today(), periods=30)
    crops_prices = {
    'Paddy':  2100 + np.cumsum(np.random.normal(0, 8, 30)),
    'Cotton': 6500 + np.cumsum(np.random.normal(0, 20, 30)),
    'Wheat':  2200 + np.cumsum(np.random.normal(0, 6, 30)),
    'Sugarcane': 3200 + np.cumsum(np.random.normal(0, 10, 30)),
    'Maize': 1900 + np.cumsum(np.random.normal(0, 7, 30)),
}

    selected_crop = st.selectbox("Select Crop", list(crops_prices.keys()))
    price_series = crops_prices[selected_crop]

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=days, y=price_series, mode='lines+markers',
                               name=selected_crop, line=dict(color='#2d6a4f', width=2)))
    fig4.add_hline(y=price_series.mean(), line_dash="dash",
                    annotation_text="Average", line_color="orange")
    fig4.update_layout(title=f"{selected_crop} — 30-Day Price Trend (₹/Quintal)",
                        xaxis_title="Date", yaxis_title="Price (₹)")
    st.plotly_chart(fig4, use_container_width=True)

    trend = "📉 Declining" if price_series[-1] < price_series[0] else "📈 Rising"
    st.info(f"**Price Trend:** {trend} | **Current:** ₹{price_series[-1]:.0f}/quintal | **30-day change:** {((price_series[-1]-price_series[0])/price_series[0]*100):.1f}%")