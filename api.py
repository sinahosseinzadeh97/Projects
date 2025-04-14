"""
API Layer for Loan Prediction System with Enhanced Features
This module provides API endpoints for all components of the loan prediction system.
"""

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime
import sys

# Create Flask app
app = Flask(__name__)

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

# Load models
try:
    model = joblib.load('models/random_forest_model.pkl')
except:
    print("Warning: Main prediction model not found. Some functionality may be limited.")

# API endpoints
@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint that processes loan parameters and returns prediction results
    """
    try:
        data = request.get_json()
        
        # Create DataFrame from input data
        input_df = pd.DataFrame([data])
        
        # Make prediction
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]
        
        # Store input data for other analyses
        session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        input_df.to_csv(f'data/sessions/{session_id}_input.csv', index=False)
        
        return jsonify({
            'session_id': session_id,
            'prediction': int(prediction),
            'probability': float(probability),
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/geographic-analysis', methods=['POST'])
def geographic_analysis():
    """
    Geographic analysis endpoint that processes location data and returns regional risk assessment
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        # Load session data if session_id is provided
        if session_id and os.path.exists(f'data/sessions/{session_id}_input.csv'):
            input_df = pd.read_csv(f'data/sessions/{session_id}_input.csv')
        else:
            input_df = pd.DataFrame([data])
        
        # Get location data
        location = data.get('location', 'Unknown')
        
        # Load regional risk data
        regional_risk_data = pd.read_csv('data/geographic/regional_risk_scores.csv')
        
        # Get regional risk score
        if location in regional_risk_data['region'].values:
            region_data = regional_risk_data[regional_risk_data['region'] == location].iloc[0].to_dict()
        else:
            # Use average if location not found
            region_data = {
                'region': location,
                'risk_score': regional_risk_data['risk_score'].mean(),
                'unemployment_rate': regional_risk_data['unemployment_rate'].mean(),
                'median_income': regional_risk_data['median_income'].mean(),
                'housing_price_index': regional_risk_data['housing_price_index'].mean()
            }
        
        # Load regional approval rates
        approval_rates = pd.read_csv('data/geographic/regional_approval_rates.csv')
        
        # Get approval rate for region
        if location in approval_rates['region'].values:
            approval_rate = float(approval_rates[approval_rates['region'] == location]['approval_rate'].iloc[0])
        else:
            approval_rate = float(approval_rates['approval_rate'].mean())
        
        # Combine results
        result = {
            'region': location,
            'risk_score': float(region_data['risk_score']),
            'unemployment_rate': float(region_data['unemployment_rate']),
            'median_income': float(region_data['median_income']),
            'housing_price_index': float(region_data['housing_price_index']),
            'approval_rate': approval_rate,
            'regional_comparison': {
                'risk_score_percentile': get_percentile(regional_risk_data['risk_score'], region_data['risk_score']),
                'unemployment_percentile': get_percentile(regional_risk_data['unemployment_rate'], region_data['unemployment_rate']),
                'income_percentile': get_percentile(regional_risk_data['median_income'], region_data['median_income']),
                'housing_percentile': get_percentile(regional_risk_data['housing_price_index'], region_data['housing_price_index'])
            },
            'status': 'success'
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/time-based-analysis', methods=['POST'])
def time_based_analysis():
    """
    Time-based analysis endpoint that processes loan parameters and returns seasonal trends and forecasts
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        # Load session data if session_id is provided
        if session_id and os.path.exists(f'data/sessions/{session_id}_input.csv'):
            input_df = pd.read_csv(f'data/sessions/{session_id}_input.csv')
        else:
            input_df = pd.DataFrame([data])
        
        # Get loan amount and term
        loan_amount = float(data.get('loan_amount', input_df['loan_amount'].iloc[0] if 'loan_amount' in input_df.columns else 10000))
        term_months = int(data.get('term', input_df['term'].iloc[0] if 'term' in input_df.columns else 36))
        interest_rate = float(data.get('interest_rate', input_df['interest_rate'].iloc[0] if 'interest_rate' in input_df.columns else 5.0))
        
        # Load seasonal trend data
        seasonal_trends = pd.read_csv('data/time_based/seasonal_loan_trends.csv')
        
        # Calculate monthly payment
        monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, term_months)
        
        # Generate repayment timeline
        timeline = generate_repayment_timeline(loan_amount, interest_rate, term_months)
        
        # Get current month
        current_month = datetime.now().month
        
        # Get seasonal factor for current month
        seasonal_factor = float(seasonal_trends[seasonal_trends['month'] == current_month]['approval_factor'].iloc[0])
        
        # Calculate adjusted approval probability based on seasonal factor
        base_approval_prob = 0.7  # Default value if not provided
        if 'probability' in data:
            base_approval_prob = float(data['probability'])
        
        adjusted_approval_prob = min(1.0, base_approval_prob * seasonal_factor)
        
        # Combine results
        result = {
            'loan_amount': loan_amount,
            'term_months': term_months,
            'interest_rate': interest_rate,
            'monthly_payment': monthly_payment,
            'total_payment': monthly_payment * term_months,
            'total_interest': (monthly_payment * term_months) - loan_amount,
            'current_month': current_month,
            'seasonal_factor': seasonal_factor,
            'base_approval_probability': base_approval_prob,
            'adjusted_approval_probability': adjusted_approval_prob,
            'repayment_timeline': timeline,
            'seasonal_trends': seasonal_trends.to_dict(orient='records'),
            'status': 'success'
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/competitive-analysis', methods=['POST'])
def competitive_analysis():
    """
    Competitive analysis endpoint that compares loan terms with market averages
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        # Load session data if session_id is provided
        if session_id and os.path.exists(f'data/sessions/{session_id}_input.csv'):
            input_df = pd.read_csv(f'data/sessions/{session_id}_input.csv')
        else:
            input_df = pd.DataFrame([data])
        
        # Get loan parameters
        loan_amount = float(data.get('loan_amount', input_df['loan_amount'].iloc[0] if 'loan_amount' in input_df.columns else 10000))
        interest_rate = float(data.get('interest_rate', input_df['interest_rate'].iloc[0] if 'interest_rate' in input_df.columns else 5.0))
        term_months = int(data.get('term', input_df['term'].iloc[0] if 'term' in input_df.columns else 36))
        credit_grade = data.get('grade', input_df['grade'].iloc[0] if 'grade' in input_df.columns else 'B')
        
        # Load market comparison data
        market_data = pd.read_csv('data/competitive/market_comparison.csv')
        
        # Filter market data by credit grade
        if credit_grade in market_data['grade'].values:
            grade_data = market_data[market_data['grade'] == credit_grade]
        else:
            grade_data = market_data
        
        # Calculate average market rates
        avg_interest_rate = float(grade_data['interest_rate'].mean())
        avg_term = float(grade_data['term'].mean())
        
        # Load alternative lenders data
        lenders_data = pd.read_csv('data/competitive/alternative_lenders.csv')
        
        # Filter lenders by credit grade
        if credit_grade in lenders_data['min_grade'].values:
            eligible_lenders = lenders_data[lenders_data['min_grade'] <= credit_grade]
        else:
            eligible_lenders = lenders_data
        
        # Sort lenders by interest rate
        eligible_lenders = eligible_lenders.sort_values('avg_interest_rate')
        
        # Calculate potential savings
        user_total_payment = calculate_monthly_payment(loan_amount, interest_rate, term_months) * term_months
        market_total_payment = calculate_monthly_payment(loan_amount, avg_interest_rate, term_months) * term_months
        best_lender_rate = float(eligible_lenders.iloc[0]['avg_interest_rate']) if len(eligible_lenders) > 0 else interest_rate
        best_lender_payment = calculate_monthly_payment(loan_amount, best_lender_rate, term_months) * term_months
        
        # Combine results
        result = {
            'user_loan': {
                'amount': loan_amount,
                'interest_rate': interest_rate,
                'term_months': term_months,
                'total_payment': user_total_payment,
                'monthly_payment': user_total_payment / term_months
            },
            'market_average': {
                'interest_rate': avg_interest_rate,
                'term_months': avg_term,
                'total_payment': market_total_payment,
                'monthly_payment': market_total_payment / term_months
            },
            'comparison': {
                'interest_rate_diff': interest_rate - avg_interest_rate,
                'payment_diff': user_total_payment - market_total_payment
            },
            'alternative_lenders': eligible_lenders.to_dict(orient='records'),
            'best_lender': {
                'name': eligible_lenders.iloc[0]['name'] if len(eligible_lenders) > 0 else 'None available',
                'interest_rate': best_lender_rate,
                'total_payment': best_lender_payment,
                'monthly_payment': best_lender_payment / term_months,
                'potential_savings': user_total_payment - best_lender_payment
            },
            'status': 'success'
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/risk-segmentation', methods=['POST'])
def risk_segmentation():
    """
    Risk segmentation endpoint that provides detailed risk profiles and tiered categorization
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        # Load session data if session_id is provided
        if session_id and os.path.exists(f'data/sessions/{session_id}_input.csv'):
            input_df = pd.read_csv(f'data/sessions/{session_id}_input.csv')
        else:
            input_df = pd.DataFrame([data])
        
        # Get key risk factors
        annual_income = float(data.get('annual_income', input_df['annual_income'].iloc[0] if 'annual_income' in input_df.columns else 50000))
        dti_ratio = float(data.get('dti_ratio', input_df['dti_ratio'].iloc[0] if 'dti_ratio' in input_df.columns else 20))
        credit_grade = data.get('grade', input_df['grade'].iloc[0] if 'grade' in input_df.columns else 'B')
        
        # Load risk tier data
        risk_tiers = pd.read_csv('data/risk_segmentation/risk_tiers.csv')
        
        # Determine risk tier
        if dti_ratio <= 20:
            risk_tier = 'Low'
        elif dti_ratio <= 35:
            risk_tier = 'Medium'
        else:
            risk_tier = 'High'
        
        # Get risk tier details
        tier_details = risk_tiers[risk_tiers['tier'] == risk_tier].iloc[0].to_dict()
        
        # Load custom scoring models
        scoring_models = pd.read_csv('data/risk_segmentation/custom_scoring_models.csv')
        
        # Determine borrower segment
        if annual_income < 30000:
            segment = 'low_income'
        elif annual_income < 100000:
            segment = 'middle_income'
        else:
            segment = 'high_income'
        
        # Get scoring model for segment
        segment_model = scoring_models[scoring_models['segment'] == segment].iloc[0].to_dict()
        
        # Calculate custom score
        income_factor = min(100, annual_income / 1000)
        dti_factor = max(0, 100 - dti_ratio)
        grade_factor = {'A': 100, 'B': 80, 'C': 60, 'D': 40, 'E': 20, 'F': 10, 'G': 0}.get(credit_grade[0], 50)
        
        custom_score = (
            income_factor * float(segment_model['income_weight']) +
            dti_factor * float(segment_model['dti_weight']) +
            grade_factor * float(segment_model['grade_weight'])
        ) / (float(segment_model['income_weight']) + float(segment_model['dti_weight']) + float(segment_model['grade_weight']))
        
        # Determine approval recommendation
        if custom_score >= 70:
            recommendation = 'Approve'
        elif custom_score >= 50:
            recommendation = 'Conditionally Approve'
        else:
            recommendation = 'Deny'
        
        # Combine results
        result = {
            'risk_profile': {
                'annual_income': annual_income,
                'dti_ratio': dti_ratio,
                'credit_grade': credit_grade,
                'custom_score': custom_score
            },
            'risk_tier': {
                'tier': risk_tier,
                'default_probability': float(tier_details['default_probability']),
                'recommended_interest_premium': float(tier_details['interest_premium']),
                'max_loan_amount': float(tier_details['max_loan_amount'])
            },
            'borrower_segment': {
                'segment': segment,
                'income_weight': float(segment_model['income_weight']),
                'dti_weight': float(segment_model['dti_weight']),
                'grade_weight': float(segment_model['grade_weight'])
            },
            'recommendation': recommendation,
            'status': 'success'
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/financial-planning', methods=['POST'])
def financial_planning():
    """
    Financial planning endpoint that provides debt consolidation analysis and retirement impact assessment
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        # Load session data if ses
(Content truncated due to size limit. Use line ranges to read in chunks)