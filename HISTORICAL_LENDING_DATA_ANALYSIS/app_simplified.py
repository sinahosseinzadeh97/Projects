from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import pandas as pd
import numpy as np
import os
import json
import secrets
import random

# Create necessary directories if they don't exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

# Load configuration
config_path = 'config/config.json'
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
else:
    config = {
        "app_name": "Loan Prediction System",
        "version": "1.0.0",
        "features": {
            "geographic_analysis": {"enabled": True},
            "time_based_analysis": {"enabled": True},
            "competitive_analysis": {"enabled": True},
            "risk_segmentation": {"enabled": True},
            "financial_planning": {"enabled": True}
        }
    }

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

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
        
        # Since we don't have a trained model, simulate prediction
        # Combine several factors to determine risk (purely illustrative)
        
        # Higher income, lower debt ratio, higher grade = lower risk
        risk_factors = []
        
        # Income factor (higher income = lower risk)
        income_factor = min(data['annual_income'] / 100000, 1.0) * 0.25
        risk_factors.append(income_factor)
        
        # Debt-to-income factor (lower ratio = lower risk)
        dti_factor = (1 - min(data['debt_to_income'] / 50, 1.0)) * 0.2
        risk_factors.append(dti_factor)
        
        # Grade factor (A=best, G=worst)
        grade_mapping = {'A': 0.2, 'B': 0.15, 'C': 0.1, 'D': 0.05, 'E': 0.0, 'F': -0.05, 'G': -0.1}
        grade_factor = grade_mapping.get(data['grade'], 0)
        risk_factors.append(grade_factor)
        
        # Employment length factor
        emp_factor = min(data['emp_length'] / 10, 1.0) * 0.15
        risk_factors.append(emp_factor)
        
        # Verification factor
        verification_mapping = {'Verified': 0.1, 'Source Verified': 0.05, 'Not Verified': 0}
        verification_factor = verification_mapping.get(data['verified_income'], 0)
        risk_factors.append(verification_factor)
        
        # Homeownership factor
        home_mapping = {'OWN': 0.1, 'MORTGAGE': 0.05, 'RENT': 0, 'OTHER': 0}
        home_factor = home_mapping.get(data['homeownership'], 0)
        risk_factors.append(home_factor)
        
        # Add some randomness (to simulate model complexity)
        random_factor = random.uniform(-0.05, 0.05)
        risk_factors.append(random_factor)
        
        # Calculate final probability (higher = better)
        probability = sum(risk_factors) + 0.5  # Baseline of 0.5
        
        # Clamp between 0 and 1
        probability = max(0.0, min(1.0, probability))
        
        # Classification
        prediction = 'Good Standing' if probability >= 0.5 else 'Default Risk'
        
        result = {
            'prediction': prediction,
            'probability': probability,
            'threshold': 0.5
        }
        
        # Store prediction in session for other features
        session['prediction_result'] = result
        
        return render_template('result.html', result=result, data=data, config=config)
    
    except Exception as e:
        return render_template('error.html', error=str(e), config=config)

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
    
    # Create dummy geographic data
    regional_economic_data = {
        "regions": {
            "Northeast": {
                "unemployment_rate": 5.2,
                "median_income": 72500,
                "housing_price_index": 342,
                "economic_growth": 1.8
            },
            "Midwest": {
                "unemployment_rate": 4.8,
                "median_income": 65400,
                "housing_price_index": 285,
                "economic_growth": 2.1
            },
            "South": {
                "unemployment_rate": 5.1,
                "median_income": 61200,
                "housing_price_index": 265,
                "economic_growth": 2.4
            },
            "West": {
                "unemployment_rate": 4.9,
                "median_income": 78300,
                "housing_price_index": 395,
                "economic_growth": 2.2
            }
        }
    }
    
    state_default_rates = {
        "states": {
            "California": 0.074,
            "Texas": 0.081,
            "New York": 0.068,
            "Florida": 0.092,
            "Illinois": 0.078,
            "Pennsylvania": 0.072,
            "Ohio": 0.085,
            "Georgia": 0.089,
            "Michigan": 0.083,
            "North Carolina": 0.076
        }
    }
    
    # Placeholder data
    loan_performance_by_region = {}
    regional_risk_scores = {}
    
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
    
    # Create dummy time-based data
    forecast_results = {
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "default_rates": [0.068, 0.072, 0.065, 0.063, 0.067, 0.071, 0.075, 0.078, 0.074, 0.069, 0.065, 0.071]
    }
    
    seasonal_trends = {
        "seasons": ["Winter", "Spring", "Summer", "Fall"],
        "application_volume": [1245, 1562, 1834, 1493],
        "approval_rates": [0.68, 0.72, 0.75, 0.71]
    }
    
    repayment_timeline_results = {
        "months_since_origination": [3, 6, 9, 12, 15, 18, 21, 24],
        "cumulative_default_rate": [0.01, 0.025, 0.042, 0.058, 0.068, 0.075, 0.079, 0.082]
    }
    
    return render_template('time_based_analysis.html', 
                          config=config,
                          forecast_results=forecast_results,
                          seasonal_trends=seasonal_trends,
                          repayment_timeline_results=repayment_timeline_results)

# Risk Segmentation Routes
@app.route('/risk-segmentation')
def risk_segmentation():
    if not config['features']['risk_segmentation']['enabled']:
        flash('Risk segmentation feature is not enabled.')
        return redirect(url_for('index'))
    
    # Create dummy risk segmentation data
    risk_tier_statistics = {
        "tiers": ["Low Risk", "Medium Risk", "High Risk", "Very High Risk"],
        "default_rates": [0.02, 0.05, 0.12, 0.25],
        "average_interest_rates": [5.2, 7.8, 12.5, 18.9],
        "population_percentage": [0.35, 0.4, 0.2, 0.05]
    }
    
    borrower_segment_statistics = {
        "segments": ["Prime", "Near-Prime", "Subprime", "Deep Subprime"],
        "approval_rates": [0.92, 0.75, 0.45, 0.15],
        "average_loan_amounts": [32500, 24200, 15800, 7500],
        "average_terms": [48, 36, 24, 12]
    }
    
    custom_scoring_models = {
        "models": ["Default", "Income-Weighted", "Credit History-Weighted", "Hybrid"],
        "accuracy": [0.82, 0.85, 0.83, 0.87],
        "precision": [0.79, 0.83, 0.8, 0.84],
        "recall": [0.81, 0.78, 0.85, 0.83]
    }
    
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
    
    # Create dummy financial planning data
    debt_management_strategies = {
        "strategies": ["Debt Snowball", "Debt Avalanche", "Debt Consolidation", "Balance Transfer"],
        "effectiveness_ratings": [8.2, 8.5, 7.8, 7.2],
        "time_to_completion": ["Medium", "Medium-Long", "Short-Medium", "Short"],
        "recommended_for": ["Motivation-seekers", "Interest minimizers", "Multiple debt holders", "High-interest debt holders"]
    }
    
    savings_recommendations = {
        "income_brackets": ["Low", "Medium", "High", "Very High"],
        "emergency_fund_months": [3, 6, 9, 12],
        "retirement_contribution_percentage": [5, 10, 15, 20],
        "debt_to_saving_ratio": [70, 50, 30, 20]
    }
    
    investment_options = {
        "risk_levels": ["Conservative", "Moderate", "Aggressive", "Very Aggressive"],
        "expected_returns": [4.5, 6.2, 8.5, 10.8],
        "recommended_allocations": {
            "Bonds": [70, 40, 20, 10],
            "Large Cap": [20, 30, 35, 30],
            "Mid Cap": [5, 15, 20, 25],
            "Small Cap": [3, 10, 15, 20],
            "International": [2, 5, 10, 15]
        }
    }
    
    # Get application data from session if available
    application_data = session.get('application_data', {})
    prediction_result = session.get('prediction_result', {})
    
    return render_template('financial_planning.html', 
                          config=config,
                          debt_management_strategies=debt_management_strategies,
                          savings_recommendations=savings_recommendations,
                          investment_options=investment_options,
                          application_data=application_data,
                          prediction_result=prediction_result)

# Competitive Analysis Routes
@app.route('/competitive-analysis')
def competitive_analysis():
    if not config['features']['competitive_analysis']['enabled']:
        flash('Competitive analysis feature is not enabled.')
        return redirect(url_for('index'))
    
    # Create dummy competitive analysis data
    lender_market_data = {
        "lenders": ["Bank A", "Bank B", "CreditUnion X", "Online Lender Y", "Peer Lender Z"],
        "market_share": [28.5, 22.3, 15.7, 18.2, 15.3],
        "average_rates": [6.8, 7.2, 5.9, 7.8, 8.5],
        "approval_criteria": ["Strict", "Moderate", "Moderate-Strict", "Flexible", "Very Flexible"]
    }
    
    industry_benchmarks = {
        "metrics": ["Default Rate", "Approval Rate", "Average Interest Rate", "Average Loan Amount", "Customer Satisfaction"],
        "industry_average": [0.082, 0.65, 7.5, 24500, 7.8],
        "top_quartile": [0.045, 0.78, 6.2, 32500, 8.9],
        "bottom_quartile": [0.125, 0.52, 9.8, 18200, 6.5]
    }
    
    alternative_lenders = {
        "lender_types": ["Traditional Banks", "Credit Unions", "Online Lenders", "Peer-to-Peer", "Microfinance"],
        "pros": [
            "Established reputation, physical branches",
            "Lower rates, personalized service",
            "Fast approval, convenient application",
            "Flexible terms, may approve lower credit scores",
            "Serves underbanked, community focus"
        ],
        "cons": [
            "Stricter requirements, slower process",
            "Limited availability, fewer products",
            "Higher rates for some, less personal",
            "Higher risk, variable rates",
            "Smaller loan amounts, higher rates"
        ]
    }
    
    return render_template('competitive_analysis.html', 
                          config=config,
                          lender_market_data=lender_market_data,
                          industry_benchmarks=industry_benchmarks,
                          alternative_lenders=alternative_lenders)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found", config=config), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Server error", config=config), 500

if __name__ == '__main__':
    # Run the app on port 5001 instead of the default 5000
    app.run(host='0.0.0.0', port=5001, debug=True) 