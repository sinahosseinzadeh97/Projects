#!/usr/bin/env python3
# Production-ready Flask Web Application for Loan Prediction

from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import pandas as pd
import os
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.middleware.proxy_fix import ProxyFix

# Create Flask application
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/loan_prediction_app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Loan Prediction App startup')

# Load the optimized model
@app.before_first_request
def load_model():
    global best_model, feature_selector, selected_feature_names, target_encoder, optimal_threshold
    
    try:
        app.logger.info("Loading optimized model...")
        with open('optimized_models.pkl', 'rb') as f:
            models = pickle.load(f)

        # Extract model components
        best_model = models['optimized_random_forest']
        feature_selector = models['feature_selector']
        selected_feature_names = models['selected_feature_names']
        target_encoder = models['target_encoder']
        optimal_threshold = models.get('optimal_threshold', 0.5)

        app.logger.info(f"Model loaded successfully. Using {len(selected_feature_names)} features.")
        app.logger.info(f"Optimal threshold: {optimal_threshold}")
    except Exception as e:
        app.logger.error(f"Error loading model: {str(e)}")
        raise

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
            app.logger.info(f"Received prediction request with data: {data}")
            
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
            
            app.logger.info(f"Prediction result: {result}")
            return render_template('result.html', result=result)
        
        except Exception as e:
            app.logger.error(f"Error making prediction: {str(e)}")
            return render_template('error.html', error=str(e))

# Add health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Add about page
@app.route('/about')
def about():
    return render_template('about.html')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {str(error)}")
    return render_template('error.html', error="Internal server error"), 500

# Run the app
if __name__ == '__main__':
    # Load model at startup
    load_model()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000)
