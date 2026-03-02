import requests

DISTRICT_COORDS = {
    "Thanjavur":  (10.7870, 79.1378),
    "Nagpur":     (21.1458, 79.0882),
    "Ludhiana":   (30.9010, 75.8573),
    "Warangal":   (17.9784, 79.5941),
    "Nashik":     (19.9975, 73.7898),
    "Pune":       (18.5204, 73.8567),
    "Amravati":   (20.9320, 77.7523),
    "Jalgaon":    (21.0077, 75.5626),
    "Nanded":     (19.1383, 77.3210),
    "Solapur":    (17.6868, 75.9067),
}

def get_weather_risk(district):
    """Fetch real weather data from Open-Meteo API (no API key required)"""
    lat, lon = DISTRICT_COORDS.get(district, (20.5937, 78.9629))
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=precipitation_sum,temperature_2m_max,temperature_2m_min"
        f"&past_days=14&forecast_days=7&timezone=Asia/Kolkata"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        daily = data['daily']

        rain_vals = [r for r in daily['precipitation_sum'] if r is not None]
        temp_vals = [t for t in daily['temperature_2m_max'] if t is not None]

        avg_rain = sum(rain_vals) / len(rain_vals) if rain_vals else 4.0
        avg_temp = sum(temp_vals) / len(temp_vals) if temp_vals else 32.0

        # India average: ~5mm/day in season; stress above 32°C
        rainfall_deviation = round(((avg_rain - 5.0) / 5.0) * 100, 1)
        temperature_stress = round(max(0, avg_temp - 32.0), 1)

        forecast_rain = daily['precipitation_sum'][-7:]
        forecast_rain = [r if r is not None else 0 for r in forecast_rain]
        forecast_summary = "Dry spell forecast" if sum(forecast_rain) < 10 else "Adequate rainfall expected"

        return {
            "rainfall_deviation": rainfall_deviation,
            "temperature_stress": temperature_stress,
            "avg_rain_mm": round(avg_rain, 2),
            "avg_temp_c": round(avg_temp, 1),
            "forecast_summary": forecast_summary,
            "source": "Open-Meteo (Live)"
        }
    except Exception as e:
        # Fallback if API unreachable
        return {
            "rainfall_deviation": -22.0,
            "temperature_stress": 3.5,
            "avg_rain_mm": 3.9,
            "avg_temp_c": 35.5,
            "forecast_summary": "Data unavailable (using fallback)",
            "source": "Fallback"
        }


def get_market_prices():
    """Simulated market price trends (replace with Agmarknet API in production)"""
    import numpy as np
    import pandas as pd
    np.random.seed(42)

    dates = pd.date_range(end=pd.Timestamp.today(), periods=30)
    crops = {
        'Paddy':     2100 + np.cumsum(np.random.normal(-2, 25, 30)),
        'Wheat':     2200 + np.cumsum(np.random.normal(-1, 20, 30)),
        'Cotton':    6500 + np.cumsum(np.random.normal(-5, 80, 30)),
        'Sugarcane': 3200 + np.cumsum(np.random.normal(1, 30, 30)),
        'Maize':     1900 + np.cumsum(np.random.normal(-3, 18, 30)),
    }
    return dates, crops