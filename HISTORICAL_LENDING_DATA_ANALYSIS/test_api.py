#!/usr/bin/env python3
"""
API Test Script for Loan Prediction System
This script tests all API endpoints to ensure they're working correctly.
"""

import requests
import json
import sys

# Base URL for API
BASE_URL = "http://localhost:5000/api"

def test_predict_endpoint():
    """Test the prediction endpoint"""
    print("\n=== Testing Prediction Endpoint ===")
    
    # Sample loan data
    loan_data = {
        "loan_amount": 10000,
        "interest_rate": 5.0,
        "term": 36,
        "grade": "B",
        "employment_length": 5,
        "annual_income": 60000,
        "dti_ratio": 20,
        "income_verification": "Verified",
        "home_ownership": "MORTGAGE",
        "total_credit_lines": 10,
        "open_credit_lines": 5,
        "mortgage_accounts": 1,
        "paid_principal": 5000,
        "paid_total": 7000
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict", json=loan_data)
        response.raise_for_status()
        result = response.json()
        
        print(f"Status: {result.get('status')}")
        print(f"Prediction: {result.get('prediction')}")
        print(f"Probability: {result.get('probability')}")
        print(f"Session ID: {result.get('session_id')}")
        
        # Return session ID for use in other tests
        return result.get('session_id')
    except Exception as e:
        print(f"Error testing prediction endpoint: {e}")
        return None

def test_geographic_analysis(session_id):
    """Test the geographic analysis endpoint"""
    print("\n=== Testing Geographic Analysis Endpoint ===")
    
    data = {
        "session_id": session_id,
        "location": "California"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/geographic-analysis", json=data)
        response.raise_for_status()
        result = response.json()
        
        print(f"Status: {result.get('status')}")
        print(f"Region: {result.get('region')}")
        print(f"Risk Score: {result.get('risk_score')}")
        print(f"Approval Rate: {result.get('approval_rate')}%")
        
        return True
    except Exception as e:
        print(f"Error testing geographic analysis endpoint: {e}")
        return False

def test_time_based_analysis(session_id):
    """Test the time-based analysis endpoint"""
    print("\n=== Testing Time-Based Analysis Endpoint ===")
    
    data = {
        "session_id": session_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/time-based-analysis", json=data)
        response.raise_for_status()
        result = response.json()
        
        print(f"Status: {result.get('status')}")
        print(f"Monthly Payment: ${result.get('monthly_payment'):.2f}")
        print(f"Total Payment: ${result.get('total_payment'):.2f}")
        print(f"Seasonal Factor: {result.get('seasonal_factor')}")
        
        return True
    except Exception as e:
        print(f"Error testing time-based analysis endpoint: {e}")
        return False

def test_competitive_analysis(session_id):
    """Test the competitive analysis endpoint"""
    print("\n=== Testing Competitive Analysis Endpoint ===")
    
    data = {
        "session_id": session_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/competitive-analysis", json=data)
        response.raise_for_status()
        result = response.json()
        
        print(f"Status: {result.get('status')}")
        user_loan = result.get('user_loan', {})
        market_avg = result.get('market_average', {})
        best_lender = result.get('best_lender', {})
        
        print(f"User Interest Rate: {user_loan.get('interest_rate')}%")
        print(f"Market Average Rate: {market_avg.get('interest_rate')}%")
        print(f"Best Lender: {best_lender.get('name')}")
        print(f"Potential Savings: ${best_lender.get('potential_savings'):.2f}")
        
        return True
    except Exception as e:
        print(f"Error testing competitive analysis endpoint: {e}")
        return False

def test_risk_segmentation(session_id):
    """Test the risk segmentation endpoint"""
    print("\n=== Testing Risk Segmentation Endpoint ===")
    
    data = {
        "session_id": session_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/risk-segmentation", json=data)
        response.raise_for_status()
        result = response.json()
        
        print(f"Status: {result.get('status')}")
        risk_profile = result.get('risk_profile', {})
        risk_tier = result.get('risk_tier', {})
        
        print(f"Custom Score: {risk_profile.get('custom_score')}")
        print(f"Risk Tier: {risk_tier.get('tier')}")
        print(f"Default Probability: {risk_tier.get('default_probability')}")
        print(f"Recommendation: {result.get('recommendation')}")
        
        return True
    except Exception as e:
        print(f"Error testing risk segmentation endpoint: {e}")
        return False

def test_financial_planning(session_id):
    """Test the financial planning endpoint"""
    print("\n=== Testing Financial Planning Endpoint ===")
    
    data = {
        "session_id": session_id,
        "debt_profile": {
            "credit_card": {"balance": 5000, "interest_rate": 18.0, "min_payment": 150},
            "car_loan": {"balance": 15000, "interest_rate": 6.0, "min_payment": 300},
            "personal_loan": {"balance": 8000, "interest_rate": 10.0, "min_payment": 200}
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/financial-planning", json=data)
        response.raise_for_status()
        result = response.json()
        
        print(f"Status: {result.get('status')}")
        current_debt = result.get('debt_consolidation', {}).get('current_debt', {})
        consolidated = result.get('debt_consolidation', {}).get('consolidated_debt', {})
        impact = result.get('debt_consolidation', {}).get('impact', {})
        
        print(f"Current Total Debt: ${current_debt.get('total_balance')}")
        print(f"Current Monthly Payment: ${current_debt.get('total_min_payment')}")
        print(f"Consolidated Monthly Payment: ${consolidated.get('monthly_payment'):.2f}")
        print(f"Monthly Savings: ${impact.get('monthly_payment_change'):.2f}")
        print(f"Interest Savings: ${impact.get('interest_savings'):.2f}")
        
        return True
    except Exception as e:
        print(f"Error testing financial planning endpoint: {e}")
        return False

def main():
    """Main function to run all tests"""
    print("=== Loan Prediction System API Test ===")
    
    # Test prediction endpoint and get session ID
    session_id = test_predict_endpoint()
    if not session_id:
        print("Failed to get session ID. Cannot continue with other tests.")
        sys.exit(1)
    
    # Test other endpoints
    tests = [
        test_geographic_analysis(session_id),
        test_time_based_analysis(session_id),
        test_competitive_analysis(session_id),
        test_risk_segmentation(session_id),
        test_financial_planning(session_id)
    ]
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Prediction Endpoint: {'Success' if session_id else 'Failed'}")
    print(f"Geographic Analysis: {'Success' if tests[0] else 'Failed'}")
    print(f"Time-Based Analysis: {'Success' if tests[1] else 'Failed'}")
    print(f"Competitive Analysis: {'Success' if tests[2] else 'Failed'}")
    print(f"Risk Segmentation: {'Success' if tests[3] else 'Failed'}")
    print(f"Financial Planning: {'Success' if tests[4] else 'Failed'}")
    
    success_count = sum([1 for test in tests if test]) + (1 if session_id else 0)
    print(f"\nOverall: {success_count}/6 tests passed")

if __name__ == "__main__":
    main()
