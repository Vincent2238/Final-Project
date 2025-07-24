# AI-Powered Real-Time Health Monitoring and Anomaly Detection System Aligned with SDG 3
# Author: Vincent Odongo
# Description: Real-time anomaly detection and personalized health insights using wearable data

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from flask import Flask, render_template, jsonify
import os

# --- Simulate Health Data ---
def simulate_health_data(num_samples=100):
    timestamps = pd.date_range(start='2023-10-01', periods=num_samples, freq='T')
    activity_level = np.random.choice(['low', 'moderate', 'high'], num_samples)
    heart_rate = [
        np.random.randint(60, 70) if act == 'low' else
        np.random.randint(71, 85) if act == 'moderate' else
        np.random.randint(86, 100)
        for act in activity_level
    ]
    blood_oxygen = np.random.randint(90, 100, num_samples)
    return pd.DataFrame({
        'timestamp': timestamps,
        'heart_rate': heart_rate,
        'blood_oxygen': blood_oxygen,
        'activity_level': activity_level
    })

# --- Anomaly Detection Model ---
def detect_anomalies(df):
    model = IsolationForest(contamination=0.1, random_state=42)
    df['anomaly_score'] = model.fit_predict(df[['heart_rate', 'blood_oxygen']])
    df['anomaly'] = df['anomaly_score'].apply(lambda x: 'Anomaly' if x == -1 else 'Normal')
    return df

# --- Train and Evaluate ---
def evaluate_model(df):
    X = df[['heart_rate', 'blood_oxygen']]
    y = df['anomaly'].apply(lambda x: 1 if x == 'Anomaly' else 0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X_train)
    y_pred = model.predict(X_test)
    y_pred = [1 if x == -1 else 0 for x in y_pred]
    return classification_report(y_test, y_pred, target_names=['Normal', 'Anomaly'])

# --- Flask App Setup ---
app = Flask(__name__)

# Simulate and process data
data = simulate_health_data()
data = detect_anomalies(data)

@app.route('/')
def index():
    latest = data.iloc[-1]
    return render_template('index.html', data={
        'timestamp': str(latest['timestamp']),
        'heart_rate': latest['heart_rate'],
        'blood_oxygen': latest['blood_oxygen'],
        'activity_level': latest['activity_level'],
        'status': latest['anomaly']
    })

@app.route('/api/metrics')
def get_metrics():
    return jsonify(data.tail(10).to_dict(orient='records'))

@app.route('/api/evaluate')
def model_evaluation():
    report = evaluate_model(data)
    return f"<pre>{report}</pre>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
