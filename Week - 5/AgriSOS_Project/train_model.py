import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle

df = pd.read_csv('farmer_data.csv')

features = ['rainfall_deviation', 'temperature_stress', 'market_price_change',
            'crop_stage', 'soil_moisture_score', 'input_expenditure_index']

X = df[features]
y = df['distress_level']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=150, random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_test)
print("Model trained!")
print(f"Accuracy: {accuracy_score(y_test, preds)*100:.1f}%")
print(classification_report(y_test, preds))

with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("model.pkl saved!")