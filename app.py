#!/usr/bin/env python3
# Flask Web Application for Loan Prediction

from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "https://loan-prediction-frontend.vercel.app",
            "https://historical-lending-data-analysis-and-loan-prediction-b5utw5emm.vercel.app"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route('/')
def index():
    return jsonify({"status": "ok", "message": "Welcome to Loan Prediction API"})

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"})

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        # Add your prediction logic here
        return jsonify({
            "status": "success",
            "prediction": "Sample prediction",
            "data_received": data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
