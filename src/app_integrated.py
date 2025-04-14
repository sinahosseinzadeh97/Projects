from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import pandas as pd
import numpy as np
import joblib
import json
import os
import sqlite3
from datetime import datetime, timedelta
import secrets

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Create necessary directories if they don't exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Load models
def load_models():
    try:
        with open('optimized_models.pkl', 'rb') as f:
            models = joblib.load(f)
        return models
    except Exception as e:
        print(f"Error loading models: {e}")
        return None

models = load_models()

# Main routes
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
        
        # Store application data in session for later use
        session['application_data'] = data
        
        # Make prediction using the model
        if models:
            best_model = models.get('optimized_random_forest')
            feature_selector = models.get('feature_selector')
            selected_feature_names = models.get('selected_feature_names')
            
            # Prepare input data
            input_df = pd.DataFrame(columns=selected_feature_names)
            input_df.loc[0] = 0  # Initialize with zeros
            
            # Fill in the values from the form
            for feature in selected_feature_names:
                if feature in data:
                    input_df.loc[0, feature] = float(data[feature])
            
            # Apply feature selection if available
            if feature_selector:
                input_selected = feature_selector.transform(input_df)
            else:
                input_selected = input_df
            
            # Make prediction
            prediction_proba = best_model.predict_proba(input_selected)[0, 1]
            prediction = 'Good Standing' if prediction_proba >= 0.5 else 'Default Risk'
            
            result = {
                'prediction': prediction,
                'probability': float(prediction_proba),
                'threshold': 0.5
            }
        else:
            # Fallback if models aren't loaded
            result = {
                'prediction': 'Unknown',
                'probability': 0.5,
                'threshold': 0.5,
                'error': 'Models not available'
            }
        
        # Store prediction in session for other features
        session['prediction_result'] = result
        
        return render_template('result.html', result=result, data=data, config=config)
    
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/about')
def about():
    return render_template('about.html', config=config)

@app.route('/documentation')
def documentation():
    return render_template('documentation.html', config=config)

# Geographic Analysis Routes
@app.route('/geographic-analysis')
def geographic_analysis():
    if not config['features']['geographic_analysis']['enabled']:
        flash('Geographic analysis feature is not enabled.')
        return redirect(url_for('index'))
    
    # Load geographic data
    regional_economic_data = {}
    state_default_rates = {}
    loan_performance_by_region = {}
    regional_risk_scores = {}
    
    try:
        with open('data/geographic/regional_economic_data.json', 'r') as f:
            regional_economic_data = json.load(f)
        
        with open('data/geographic/state_default_rates.json', 'r') as f:
            state_default_rates = json.load(f)
        
        with open('data/geographic/loan_performance_by_region.json', 'r') as f:
            loan_performance_by_region = json.load(f)
        
        with open('data/geographic/regional_risk_scores.json', 'r') as f:
            regional_risk_scores = json.load(f)
    except Exception as e:
        flash(f'Error loading geographic data: {str(e)}')
    
    return render_template('geographic_analysis.html', 
                          config=config,
                          regional_economic_data=regional_economic_data,
                          state_default_rates=state_default_rates,
                          loan_performance_by_region=loan_performance_by_region,
                          regional_risk_scores=regional_risk_scores)

# Time-Based Analysis Routes
@app.route('/time-based-analysis')
def time_based_analysis():
    if not config['features']['time_based_analysis']['enabled']:
        flash('Time-based analysis feature is not enabled.')
        return redirect(url_for('index'))
    
    # Load time-based data
    forecast_results = {}
    seasonal_trends = {}
    repayment_timeline_results = {}
    
    try:
        with open('data/time_based/forecast_results.json', 'r') as f:
            forecast_results = json.load(f)
        
        with open('data/time_based/seasonal_trends.json', 'r') as f:
            seasonal_trends = json.load(f)
        
        with open('data/time_based/repayment_timeline_results.json', 'r') as f:
            repayment_timeline_results = json.load(f)
    except Exception as e:
        flash(f'Error loading time-based data: {str(e)}')
    
    return render_template('time_based_analysis.html', 
                          config=config,
                          forecast_results=forecast_results,
                          seasonal_trends=seasonal_trends,
                          repayment_timeline_results=repayment_timeline_results)

# Competitive Analysis Routes
@app.route('/competitive-analysis')
def competitive_analysis():
    if not config['features']['competitive_analysis']['enabled']:
        flash('Competitive analysis feature is not enabled.')
        return redirect(url_for('index'))
    
    # Load competitive analysis data
    lender_market_data = {}
    industry_benchmarks = {}
    alternative_lenders = {}
    
    try:
        with open('data/competitive/lender_market_data.json', 'r') as f:
            lender_market_data = json.load(f)
        
        with open('data/competitive/industry_benchmarks.json', 'r') as f:
            industry_benchmarks = json.load(f)
        
        with open('data/competitive/alternative_lenders.json', 'r') as f:
            alternative_lenders = json.load(f)
    except Exception as e:
        flash(f'Error loading competitive analysis data: {str(e)}')
    
    return render_template('competitive_analysis.html', 
                          config=config,
                          lender_market_data=lender_market_data,
                          industry_benchmarks=industry_benchmarks,
                          alternative_lenders=alternative_lenders)

# Risk Segmentation Routes
@app.route('/risk-segmentation')
def risk_segmentation():
    if not config['features']['risk_segmentation']['enabled']:
        flash('Risk segmentation feature is not enabled.')
        return redirect(url_for('index'))
    
    # Load risk segmentation data
    risk_tier_statistics = {}
    borrower_segment_statistics = {}
    custom_scoring_models = {}
    
    try:
        with open('data/risk_segmentation/risk_tier_statistics.json', 'r') as f:
            risk_tier_statistics = json.load(f)
        
        with open('data/risk_segmentation/borrower_segment_statistics.json', 'r') as f:
            borrower_segment_statistics = json.load(f)
        
        with open('data/risk_segmentation/custom_scoring_models.json', 'r') as f:
            custom_scoring_models = json.load(f)
    except Exception as e:
        flash(f'Error loading risk segmentation data: {str(e)}')
    
    # Get application data from session if available
    application_data = session.get('application_data', {})
    prediction_result = session.get('prediction_result', {})
    
    return render_template('risk_segmentation.html', 
                          config=config,
                          risk_tier_statistics=risk_tier_statistics,
                          borrower_segment_statistics=borrower_segment_statistics,
                          custom_scoring_models=custom_scoring_models,
                          application_data=application_data,
                          prediction_result=prediction_result)

# Financial Planning Routes
@app.route('/financial-planning')
def financial_planning():
    if not config['features']['financial_planning']['enabled']:
        flash('Financial planning feature is not enabled.')
        return redirect(url_for('index'))
    
    # Load financial planning data
    debt_profiles = {}
    consolidation_options = {}
    retirement_scenarios = {}
    
    try:
        with open('data/financial_planning/debt_profiles.json', 'r') as f:
            debt_profiles = json.load(f)
        
        with open('data/financial_planning/consolidation_options.json', 'r') as f:
            consolidation_options = json.load(f)
        
        with open('data/financial_planning/retirement_scenarios.json', 'r') as f:
            retirement_scenarios = json.load(f)
    except Exception as e:
        flash(f'Error loading financial planning data: {str(e)}')
    
    # Get application data from session if available
    application_data = session.get('application_data', {})
    
    return render_template('financial_planning.html', 
                          config=config,
                          debt_profiles=debt_profiles,
                          consolidation_options=consolidation_options,
                          retirement_scenarios=retirement_scenarios,
                          application_data=application_data)

# Dashboard with all features
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', config=config)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Internal server error'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
