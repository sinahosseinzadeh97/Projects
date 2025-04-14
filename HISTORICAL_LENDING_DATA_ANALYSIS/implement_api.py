import os
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from flask import Flask, request, jsonify, make_response
import jwt
from functools import wraps

print("Starting implementation of API integration capabilities...")

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

# Update configuration to enable API
config['features']['api']['enabled'] = True
with open('config/config.json', 'w') as f:
    json.dump(config, f, indent=4)

print("API integration enabled in configuration")

# Create API module
api_module = '''from flask import Blueprint, request, jsonify, current_app
import jwt
import datetime
from functools import wraps
import sqlite3
import json
import os
import joblib
import numpy as np
import pandas as pd
from utils.recommendation_engine import LoanRecommendationEngine

# Create API blueprint
api = Blueprint('api', __name__)

# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Decode token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            
            # Get user from database
            conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (data['user_id'],))
            current_user = dict(cursor.fetchone())
            
            conn.close()
            
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# API routes
@api.route('/login', methods=['POST'])
def login():
    auth = request.json
    
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic realm="Login required!"'}), 401
    
    conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (auth.get('username'),))
    user = cursor.fetchone()
    
    conn.close()
    
    if not user:
        return jsonify({'message': 'User not found!'}), 401
    
    # In a real application, we would verify the password hash
    # For this demo, we'll just check if the password matches
    if user['password_hash'] != auth.get('password'):
        return jsonify({'message': 'Invalid password!'}), 401
    
    # Generate token
    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({'token': token})

@api.route('/predict', methods=['POST'])
@token_required
def predict(current_user):
    data = request.json
    
    if not data:
        return jsonify({'message': 'No data provided!'}), 400
    
    required_fields = ['loan_amount', 'interest_rate', 'term', 'grade', 'emp_length', 
                      'annual_income', 'debt_to_income', 'verified_income', 'homeownership',
                      'total_credit_lines', 'open_credit_lines', 'num_mort_accounts',
                      'paid_principal', 'paid_total']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    try:
        # Load model
        model_path = os.path.join(current_app.config['MODEL_PATH'], 'ensemble_model.pkl')
        preprocessor_path = os.path.join(current_app.config['MODEL_PATH'], 'preprocessor.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
            return jsonify({'message': 'Model not found!'}), 500
        
        model = joblib.load(model_path)
        preprocessor = joblib.load(preprocessor_path)
        
        # Prepare data for prediction
        df = pd.DataFrame([data])
        
        # Preprocess data
        X = preprocessor.transform(df)
        
        # Make prediction
        prediction_proba = model.predict_proba(X)[0]
        prediction = model.predict(X)[0]
        
        # Save prediction to database
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()
        
        # Insert application
        cursor.execute("""
            INSERT INTO loan_applications
            (user_id, loan_amount, interest_rate, term, grade, emp_length,
             annual_income, debt_to_income, verified_income, homeownership,
             total_credit_lines, open_credit_lines, num_mort_accounts,
             paid_principal, paid_total, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            current_user['id'],
            data['loan_amount'],
            data['interest_rate'],
            data['term'],
            data['grade'],
            data['emp_length'],
            data['annual_income'],
            data['debt_to_income'],
            data['verified_income'],
            data['homeownership'],
            data['total_credit_lines'],
            data['open_credit_lines'],
            data['num_mort_accounts'],
            data['paid_principal'],
            data['paid_total'],
            datetime.datetime.now()
        ))
        
        application_id = cursor.lastrowid
        
        # Insert prediction
        cursor.execute("""
            INSERT INTO predictions
            (application_id, model_name, prediction, probability, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            application_id,
            'ensemble',
            'Stand-standing' if prediction == 1 else 'Default',
            float(prediction_proba[1]) if prediction == 1 else float(prediction_proba[0]),
            datetime.datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        # Return prediction
        return jsonify({
            'application_id': application_id,
            'prediction': 'Good Standing' if prediction == 1 else 'Default Risk',
            'probability': float(prediction_proba[1]) if prediction == 1 else float(prediction_proba[0]),
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'message': 'Error making prediction!', 'error': str(e)}), 500

@api.route('/recommendations', methods=['GET'])
@token_required
def get_recommendations(current_user):
    try:
        # Get user's financial profile
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM loan_applications 
            WHERE user_id = ? 
            ORDER BY created_at DESC
            LIMIT 1
        """, (current_user['id'],))
        
        profile = cursor.fetchone()
        conn.close()
        
        if not profile:
            return jsonify({'message': 'No profile found!'}), 404
        
        profile = dict(profile)
        
        # Create recommendation engine
        engine = LoanRecommendationEngine()
        
        # Generate recommendations
        recommendations = engine.generate_recommendations(profile)
        
        return jsonify({
            'user_id': current_user['id'],
            'recommendations': recommendations,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'message': 'Error generating recommendations!', 'error': str(e)}), 500

@api.route('/applications', methods=['GET'])
@token_required
def get_applications(current_user):
    try:
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM loan_applications 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (current_user['id'],))
        
        applications = [dict(row) for row in cursor.fetchall()]
        
        # Get predictions for each application
        for app in applications:
            cursor.execute("""
                SELECT * FROM predictions
                WHERE application_id = ?
                ORDER BY created_at DESC
            """, (app['id'],))
            
            app['predictions'] = [dict(row) for row in cursor.fetchall()]
            
            # Convert datetime to string
            app['created_at'] = app['created_at'] if isinstance(app['created_at'], str) else str(app['created_at'])
            
            for pred in app['predictions']:
                pred['created_at'] = pred['created_at'] if isinstance(pred['created_at'], str) else str(pred['created_at'])
        
        conn.close()
        
        return jsonify({
            'user_id': current_user['id'],
            'applications': applications,
            'count': len(applications),
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'message': 'Error retrieving applications!', 'error': str(e)}), 500

@api.route('/what-if', methods=['POST'])
@token_required
def what_if_analysis(current_user):
    data = request.json
    
    if not data:
        return jsonify({'message': 'No data provided!'}), 400
    
    required_fields = ['loan_amount', 'interest_rate', 'term']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    try:
        # Get user's financial profile
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM loan_applications 
            WHERE user_id = ? 
            ORDER BY created_at DESC
            LIMIT 1
        """, (current_user['id'],))
        
        profile = cursor.fetchone()
        conn.close()
        
        if not profile:
            return jsonify({'message': 'No profile found!'}), 404
        
        profile = dict(profile)
        
        # Create recommendation engine
        engine = LoanRecommendationEngine()
        
        # Perform what-if analysis
        result = engine.what_if_analysis(data, profile)
        
        return jsonify({
            'user_id': current_user['id'],
            'loan_params': data,
            'analysis_result': result,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'message': 'Error performing what-if analysis!', 'error': str(e)}), 500

@api.route('/batch-predict', methods=['POST'])
@token_required
def batch_predict(current_user):
    data = request.json
    
    if not data or not isinstance(data, list):
        return jsonify({'message': 'Invalid data format! Expected a list of applications.'}), 400
    
    if len(data) > current_app.config['MAX_BATCH_SIZE']:
        return jsonify({'message': f'Batch size exceeds maximum allowed ({current_app.config["MAX_BATCH_SIZE"]})!'}), 400
    
    required_fields = ['loan_amount', 'interest_rate', 'term', 'grade', 'emp_length', 
                      'annual_income', 'debt_to_income', 'verified_income', 'homeownership',
                      'total_credit_lines', 'open_credit_lines', 'num_mort_accounts',
                      'paid_principal', 'paid_total']
    
    for i, app in enumerate(data):
        for field in required_fields:
            if field not in app:
                return jsonify({'message': f'Missing required field: {field} in application at index {i}'}), 400
    
    try:
        # Load model
        model_path = os.path.join(current_app.config['MODEL_PATH'], 'ensemble_model.pkl')
        preprocessor_path = os.path.join(current_app.config['MODEL_PATH'], 'preprocessor.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
            return jsonify({'message': 'Model not found!'}), 500
        
        model = joblib.load(model_path)
        preprocessor = joblib.load(preprocessor_path)
        
        # Prepare data for prediction
        df = pd.DataFrame(data)
        
        # Preprocess data
        X = preprocessor.transform(df)
        
        # Make predictions
        predictions_proba = model.predict_proba(X)
        predictions = model.predict(X)
        
        # Save predictions to database
        conn = sqlite3.connect(current_app.config['DATABASE_PATH'])
        cursor = conn.cursor()
        
        results = []
        
        for i, app in enumerate(data):
            # Insert application
            cursor.execute("""
                INSERT INTO loan_applications
                (user_id, loan_amount, interest_rate, term, grade, emp_length,
                 annual_income, debt_to_income, verified_income, homeownership,
                 total_credit_lines, open_credit_lines, num_mort_accounts,
                 paid_principal, paid_total, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                current_user['id'],
                app['loan_amount'],
                app['interest_rate'],
                app['term'],
                app['grade'],
                app['emp_length'],
                app['annual_income'],
                app['debt_to_income'],
                app['verified_income'],
                app['homeownership'],
                app['total_credit_lines'],
                app['open_credit_lines'],
                app['num_mort_accounts'],
                app['paid_principal'],
                app['paid_total'],
                datetime.datetime.now()
            ))
            
            application_id = cursor.lastrowid
            
            # Insert prediction
            cursor.execute("""
                INSERT INTO predictions
                (application_id, model_name, prediction, probability, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                application_id,
                'ensemble',
                'Stand-standing' if predictions[i] == 1 else 'Default',
                float(predictions_proba[i][1]) if predictions[i] == 1 else float(predictions_proba[i][0]),
                datetime.datetime.now()
            ))
            
            # Add to results
            results.append({
                'application_id': application_id,
                'prediction': 'Good Standing' if predictions[i] == 1 else 'Default Risk',
                'probability': float(predictions_proba[i][1]) if predictions[i] == 1 else float(predictions_proba[i][0])
            })
        
        conn.commit()
        conn.close()
        
        # Return predictions
        return jsonify({
            'batch_size': len(data),
            'results': results,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'message': 'Error processing batch prediction!', 'error': str(e)}), 500

@api.route('/export', methods=['GET'])
@token_required
def export_data(current_user):
    format_type = request.args.get('format', 'json')
    
    if format_type not in ['json', 'csv']:
        return jsonify({'message': 'Invalid format! Supported formats: json, csv'}), 400
    
    try:
   
(Content truncated due to size limit. Use line ranges to read in chunks)