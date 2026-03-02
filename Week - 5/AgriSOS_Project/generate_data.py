import pandas as pd
import numpy as np

np.random.seed(42)
n = 600

df = pd.DataFrame({
    'rainfall_deviation': np.random.uniform(-60, 20, n),
    'temperature_stress': np.random.uniform(0, 10, n),
    'market_price_change': np.random.uniform(-40, 15, n),
    'crop_stage': np.random.randint(1, 5, n),
    'soil_moisture_score': np.random.uniform(1, 10, n),
    'input_expenditure_index': np.random.uniform(0.5, 2.5, n),
})

def label(row):
    score = 0
    if row['rainfall_deviation'] < -30: score += 35
    elif row['rainfall_deviation'] < -15: score += 20
    if row['temperature_stress'] > 6: score += 20
    elif row['temperature_stress'] > 3: score += 10
    if row['market_price_change'] < -20: score += 25
    elif row['market_price_change'] < -10: score += 15
    if row['crop_stage'] == 3: score += 10
    if row['soil_moisture_score'] < 3: score += 10
    if row['input_expenditure_index'] > 2: score += 10
    if score >= 60: return 'High'
    elif score >= 35: return 'Medium'
    else: return 'Low'

df['distress_level'] = df.apply(label, axis=1)
df.to_csv('farmer_data.csv', index=False)
print("Dataset created!")
print(df['distress_level'].value_counts())