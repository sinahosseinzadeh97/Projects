#!/usr/bin/env python3
# Flask Web Application for Loan Prediction

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import joblib
import numpy as np
import os

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates')

# Configure CORS to allow requests from your Vercel frontend
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "https://frontend-jzhumzu8j-sinahosseinzadeh20-gmailcoms-projects.vercel.app",
            "https://loan-prediction-frontend.vercel.app"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Load the model
try:
    model = joblib.load('model.joblib')
except:
    model = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/health', methods=['GET'])
def health_check():
    if model is None:
        return jsonify({
            'status': 'error',
            'message': 'Model not loaded'
        }), 500
    
    return jsonify({
        'status': 'success',
        'message': 'API is running and model is loaded'
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        if model is None:
            return jsonify({
                'status': 'error',
                'message': 'Model not loaded'
            }), 500

        data = request.get_json()
        
        # Extract features matching the frontend form
        features = np.array([
            float(data['loan_amount']),
            float(data['interest_rate']),
            float(data['term']),
            float(data['emp_length']),
            float(data['annual_income']),
            float(data['debt_to_income']),
            1 if data['verified_income'] == 'Verified' else 0,
            1 if data['homeownership'] == 'OWN' else 0,
            float(data['total_credit_lines']),
            float(data['open_credit_lines']),
            float(data['num_mort_accounts']),
            float(data['paid_principal']),
            float(data['paid_total'])
        ]).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(features)[0]
        
        return jsonify({
            'status': 'success',
            'prediction': int(prediction)
        })
    except KeyError as e:
        return jsonify({
            'status': 'error',
            'message': f'Missing required field: {str(e)}'
        }), 400
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'Invalid value provided: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
