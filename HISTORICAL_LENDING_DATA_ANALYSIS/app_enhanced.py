from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import pandas as pd
import numpy as np
import joblib
import json
import os
import sqlite3
from datetime import datetime, timedelta
import secrets
from api.routes import api
from utils.model_utils import load_models
from utils.data_utils import prepare_data_for_prediction, store_application

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.register_blueprint(api)

# Load models
model_names = config['models']['ensemble']['models']
models = load_models(model_names)
if 'ensemble' in models:
    ensemble_model = models['ensemble']
else:
    ensemble_model = models.get(model_names[0]) if model_names else None

@app.route('/')
def index():
    return render_template('index.html', config=config)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        data = {
            'loan_amount': float(request.form['loan_amount']),
            'interest_rate': float(request.form['interest_rate']),
            'term': int(request.form['term']),
            'grade': request.form['grade'],
            'emp_length': int(request.form['emp_length']),
            'annual_income': float(request.form['annual_income']),
            'debt_to_income': float(request.form['debt_to_income']),
            'verified_income': request.form['verified_income'],
            'homeownership': request.form['homeownership'],
            'total_credit_lines': int(request.form['total_credit_lines']),
            'open_credit_lines': int(request.form['open_credit_lines']),
            'num_mort_accounts': int(request.form['num_mort_accounts']),
            'paid_principal': float(request.form['paid_principal']),
            'paid_total': float(request.form['paid_total'])
        }
        
        # Store application in database
        user_id = session.get('user_id')
        application_id = store_application(data, user_id)
        data['application_id'] = application_id
        
        # Prepare data for prediction
        input_data = prepare_data_for_prediction(data)
        
        # Make predictions with available models
        results = {}
        for name, model in models.items():
            try:
                probability = model.predict_proba(input_data)[0][1]
                prediction = 'Stand-standing' if probability >= 0.5 else 'Default'
                results[name] = {
                    'prediction': prediction,
                    'probability': float(probability)
                }
            except Exception as e:
                results[name] = {
                    'error': str(e)
                }
        
        # Use ensemble model if available, otherwise use first available model
        if 'ensemble' in results:
            result = results['ensemble']
        else:
            result = next(iter(results.values()))
        
        # Store prediction in session for report generation
        session['last_prediction'] = {
            'data': data,
            'result': result,
            'all_results': results
        }
        
        return render_template('result.html', 
                              prediction=result['prediction'],
                              probability=result['probability'],
                              data=data,
                              all_results=results,
                              config=config)
    
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/report')
def report():
    # Get last prediction from session
    prediction_data = session.get('last_prediction')
    
    if not prediction_data:
        flash('No prediction data available. Please make a prediction first.')
        return redirect(url_for('index'))
    
    return render_template('report.html',
                          data=prediction_data['data'],
                          result=prediction_data['result'],
                          all_results=prediction_data['all_results'],
                          config=config)

@app.route('/dashboard')
def dashboard():
    if not config['features']['dashboard']['enabled']:
        flash('Dashboard feature is not enabled yet.')
        return redirect(url_for('index'))
    
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id and config['features']['user_accounts']['enabled']:
        flash('Please log in to access the dashboard.')
        return redirect(url_for('login'))
    
    # Get user's applications
    conn = sqlite3.connect('data/loan_prediction.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute("""
            SELECT * FROM loan_applications 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user_id,))
    else:
        # For demo purposes, get all applications
        cursor.execute("""
            SELECT * FROM loan_applications 
            ORDER BY created_at DESC
            LIMIT 10
        """)
    
    applications = [dict(row) for row in cursor.fetchall()]
    
    # Get predictions for each application
    for app in applications:
        cursor.execute("""
            SELECT * FROM predictions
            WHERE application_id = ?
            ORDER BY created_at DESC
        """, (app['id'],))
        
        app['predictions'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('dashboard.html',
                          applications=applications,
                          config=config)

@app.route('/compare')
def compare():
    if not config['features']['comparison']['enabled']:
        flash('Comparison feature is not enabled yet.')
        return redirect(url_for('index'))
    
    return render_template('compare.html', config=config)

@app.route('/about')
def about():
    return render_template('about.html', config=config)

@app.route('/documentation')
def documentation():
    return render_template('documentation.html', config=config)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not config['features']['user_accounts']['enabled']:
        flash('User accounts feature is not enabled yet.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('data/loan_prediction.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user and user[1] == password:  # In production, use proper password hashing
            session['user_id'] = user[0]
            session['username'] = username
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                          (datetime.now(), user[0]))
            conn.commit()
            
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
        
        conn.close()
    
    return render_template('login.html', config=config)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if not config['features']['user_accounts']['enabled']:
        flash('User accounts feature is not enabled yet.')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('data/loan_prediction.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
                (username, email, password, datetime.now())  # In production, hash the password
            )
            conn.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists')
        finally:
            conn.close()
    
    return render_template('register.html', config=config)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/api-docs')
def api_docs():
    if not config['api']['enable_documentation']:
        flash('API documentation is not enabled.')
        return redirect(url_for('index'))
    
    return render_template('api_docs.html', config=config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
