#!/usr/bin/env python3
# Flask Web Application for Loan Prediction

from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import pandas as pd
import os

app = Flask(__name__)

# Load the optimized model
print("Loading optimized model...")
with open('optimized_models.pkl', 'rb') as f:
    models = pickle.load(f)

# Extract model components
best_model = models['optimized_random_forest']
feature_selector = models['feature_selector']
selected_feature_names = models['selected_feature_names']
target_encoder = models['target_encoder']
optimal_threshold = models.get('optimal_threshold', 0.5)

print(f"Model loaded successfully. Using {len(selected_feature_names)} features.")
print(f"Optimal threshold: {optimal_threshold}")

# Define the home page route
@app.route('/')
def home():
    return render_template('index.html')

# Define the prediction route
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # Get form data
            data = request.form.to_dict()
            
            # Create a DataFrame with all features (will be filtered by feature_selector)
            input_df = pd.DataFrame(columns=selected_feature_names)
            input_df.loc[0] = 0  # Initialize with zeros
            
            # Fill in the values from the form
            for feature in selected_feature_names:
                if feature in data:
                    input_df.loc[0, feature] = float(data[feature])
            
            # Apply feature selection
            input_selected = feature_selector.transform(input_df)
            
            # Make prediction
            prediction_proba = best_model.predict_proba(input_selected)[0, 1]
            prediction = 1 if prediction_proba >= optimal_threshold else 0
            
            # Convert prediction to label
            prediction_label = target_encoder.inverse_transform([prediction])[0]
            
            # Prepare result
            result = {
                'prediction': prediction_label,
                'probability': float(prediction_proba),
                'threshold': float(optimal_threshold)
            }
            
            return render_template('result.html', result=result)
        
        except Exception as e:
            return render_template('error.html', error=str(e))

# Run the app
if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
