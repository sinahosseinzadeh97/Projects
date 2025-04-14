#!/usr/bin/env python3
# Flask Web Application for Loan Prediction

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# More permissive CORS configuration
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    try:
        logger.info("Accessing root endpoint")
        return jsonify({"status": "ok", "message": "Welcome to Loan Prediction API"})
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/health')
def health_check():
    try:
        logger.info("Accessing health check endpoint")
        return jsonify({
            "status": "healthy",
            "message": "API is running",
            "version": "1.0.0"
        })
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

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
