#!/usr/bin/env python3
# Flask Web Application for Loan Prediction

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# Load the model
try:
    model = joblib.load('model.joblib')
except:
    model = None

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        # Extract features
        features = np.array([
            float(data['creditScore']),
            float(data['income']),
            float(data['loanAmount']),
            float(data['loanTerm']),
            float(data['employmentLength'])
        ]).reshape(1, -1)
        
        if model is None:
            return jsonify({
                'status': 'error',
                'message': 'Model not loaded'
            }), 500
            
        # Make prediction
        prediction = model.predict(features)[0]
        
        return jsonify({
            'status': 'success',
            'prediction': int(prediction)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
