#!/usr/bin/env python3
# Static Flask Web Application for Loan Prediction (JavaScript-based prediction)

from flask import Flask, render_template, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_url_path='/static')

# Define the home page route
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Serve static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Add health check endpoint
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Run the app
if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
