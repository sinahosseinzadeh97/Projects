"""
Financial Planning Integration Module for Loan Prediction System
Implements debt consolidation analysis, retirement impact assessment,
and long-term financial health projections.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import minimize
import os
import json
from datetime import datetime, timedelta

# Create directories if they don't exist
os.makedirs('data/financial_planning', exist_ok=True)
os.makedirs('static/img/financial_planning', exist_ok=True)

# Function to perform debt consolidation analysis
def perform_debt_consolidation_analysis():
    # Sample debt profiles for analysis
    debt_profiles = {
        'Profile 1': {
            'credit_card_1': {'balance': 8500, 'interest_rate': 22.99, 'min_payment': 250},
            'credit_card_2': {'balance': 4200, 'interest_rate': 19.99, 'min_payment': 120},
            'personal_loan': {'balance': 12000, 'interest_rate': 12.5, 'min_payment': 350},
            'auto_loan': {'balance': 18000, 'interest_rate': 6.5, 'min_payment': 400}
        },
        'Profile 2': {
            'credit_card_1': {'balance': 15000, 'interest_rate': 24.99, 'min_payment': 450},
            'credit_card_2': {'balance': 7500, 'interest_rate': 21.99, 'min_payment': 225},
            'credit_card_3': {'balance': 3200, 'interest_rate': 18.99, 'min_payment': 100},
            'personal_loan': {'balance': 8000, 'interest_rate': 10.5, 'min_payment': 250}
        },
        'Profile 3': {
            'student_loan_1': {'balance': 25000, 'interest_rate': 5.8, 'min_payment': 280},
            'student_loan_2': {'balance': 18000, 'interest_rate': 6.2, 'min_payment': 210},
            'credit_card': {'balance': 6500, 'interest_rate': 17.99, 'min_payment': 200},
            'personal_loan': {'balance': 10000, 'interest_rate': 11.5, 'min_payment': 300}
        }
    }
    
    # Save debt profiles to JSON
    with open('data/financial_planning/debt_profiles.json', 'w') as f:
        json.dump(debt_profiles, f, indent=4)
    
    # Consolidation loan options
    consolidation_options = {
        'Option A': {'interest_rate': 8.99, 'term_years': 3, 'origination_fee_pct': 1.5},
        'Option B': {'interest_rate': 10.49, 'term_years': 5, 'origination_fee_pct': 0.0},
        'Option C': {'interest_rate': 7.99, 'term_years': 3, 'origination_fee_pct': 2.5},
        'Option D': {'interest_rate': 9.49, 'term_years': 5, 'origination_fee_pct': 1.0}
    }
    
    # Save consolidation options to JSON
    with open('data/financial_planning/consolidation_options.json', 'w') as f:
        json.dump(consolidation_options, f, indent=4)
    
    # Analyze each debt profile with each consolidation option
    results = {}
    
    for profile_name, debts in debt_profiles.items():
        profile_results = {}
        
        # Calculate current debt statistics
        total_debt = sum(debt['balance'] for debt in debts.values())
        weighted_avg_rate = sum(debt['balance'] * debt['interest_rate'] for debt in debts.values()) / total_debt
        total_min_payment = sum(debt['min_payment'] for debt in debts.values())
        
        # Calculate time to payoff and total interest with minimum payments
        months_to_payoff, total_interest = calculate_debt_payoff(debts, payment_strategy='minimum')
        
        # Calculate time to payoff and total interest with avalanche method (highest interest first)
        avalanche_months, avalanche_interest = calculate_debt_payoff(debts, payment_strategy='avalanche')
        
        # Calculate time to payoff and total interest with snowball method (smallest balance first)
        snowball_months, snowball_interest = calculate_debt_payoff(debts, payment_strategy='snowball')
        
        # Store current debt statistics
        profile_results['current'] = {
            'total_debt': total_debt,
            'weighted_avg_rate': weighted_avg_rate,
            'total_min_payment': total_min_payment,
            'months_to_payoff_minimum': months_to_payoff,
            'total_interest_minimum': total_interest,
            'months_to_payoff_avalanche': avalanche_months,
            'total_interest_avalanche': avalanche_interest,
            'months_to_payoff_snowball': snowball_months,
            'total_interest_snowball': snowball_interest
        }
        
        # Analyze each consolidation option
        for option_name, option in consolidation_options.items():
            # Calculate consolidation loan details
            origination_fee = total_debt * (option['origination_fee_pct'] / 100)
            loan_amount = total_debt + origination_fee
            term_months = option['term_years'] * 12
            monthly_rate = option['interest_rate'] / 100 / 12
            monthly_payment = loan_amount * monthly_rate * (1 + monthly_rate) ** term_months / ((1 + monthly_rate) ** term_months - 1)
            total_payments = monthly_payment * term_months
            total_interest = total_payments - total_debt
            
            # Store consolidation option results
            profile_results[option_name] = {
                'loan_amount': loan_amount,
                'origination_fee': origination_fee,
                'interest_rate': option['interest_rate'],
                'term_months': term_months,
                'monthly_payment': monthly_payment,
                'total_payments': total_payments,
                'total_interest': total_interest
            }
        
        results[profile_name] = profile_results
    
    # Save analysis results to JSON
    with open('data/financial_planning/debt_consolidation_analysis.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    # Create visualizations
    for profile_name, profile_results in results.items():
        # Comparison of total interest paid
        plt.figure(figsize=(12, 6))
        
        # Extract options and interest amounts
        options = list(profile_results.keys())
        interest_amounts = [profile_results[option].get('total_interest', profile_results[option].get('total_interest_minimum', 0)) 
                           for option in options]
        
        # Create bar chart
        bars = plt.bar(options, interest_amounts)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 500,
                    f'${height:,.0f}',
                    ha='center', va='bottom', rotation=0)
        
        plt.title(f'Total Interest Paid - {profile_name}')
        plt.ylabel('Total Interest ($)')
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'static/img/financial_planning/interest_comparison_{profile_name.replace(" ", "_").lower()}.png')
        plt.close()
        
        # Comparison of monthly payments
        plt.figure(figsize=(12, 6))
        
        # Extract options and monthly payments
        options = list(profile_results.keys())
        monthly_payments = []
        
        for option in options:
            if option == 'current':
                monthly_payments.append(profile_results[option]['total_min_payment'])
            else:
                monthly_payments.append(profile_results[option]['monthly_payment'])
        
        # Create bar chart
        bars = plt.bar(options, monthly_payments)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 20,
                    f'${height:,.0f}',
                    ha='center', va='bottom', rotation=0)
        
        plt.title(f'Monthly Payment Comparison - {profile_name}')
        plt.ylabel('Monthly Payment ($)')
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'static/img/financial_planning/payment_comparison_{profile_name.replace(" ", "_").lower()}.png')
        plt.close()
    
    # Create summary visualization
    plt.figure(figsize=(15, 8))
    
    # Prepare data for grouped bar chart
    profiles = list(results.keys())
    options = ['current', 'Option A', 'Option B', 'Option C', 'Option D']
    
    # Set up positions for grouped bars
    x = np.arange(len(profiles))
    width = 0.15
    
    # Plot bars for each option
    for i, option in enumerate(options):
        interest_values = []
        
        for profile in profiles:
            if option == 'current':
                interest_values.append(results[profile][option]['total_interest_avalanche'])
            else:
                if option in results[profile]:
                    interest_values.append(results[profile][option]['total_interest'])
                else:
                    interest_values.append(0)
        
        plt.bar(x + (i - 2) * width, interest_values, width, label=option)
    
    plt.title('Total Interest Comparison Across Debt Profiles and Consolidation Options')
    plt.xlabel('Debt Profile')
    plt.ylabel('Total Interest ($)')
    plt.xticks(x, profiles)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('static/img/financial_planning/consolidation_comparison_summary.png')
    plt.close()
    
    return results

# Helper function to calculate debt payoff timeline and interest
def calculate_debt_payoff(debts, payment_strategy='minimum'):
    # Create a copy of the debts to work with
    debts_copy = {}
    for debt_name, debt in debts.items():
        debts_copy[debt_name] = debt.copy()
    
    # Calculate total minimum payment
    total_min_payment = sum(debt['min_payment'] for debt in debts_copy.values())
    
    # Initialize tracking variables
    months = 0
    total_interest = 0
    remaining_debt = sum(debt['balance'] for debt in debts_copy.values())
    
    # Continue until all debts are paid off
    while remaining_debt > 0 and months < 600:  # Cap at 50 years to prevent infinite loops
        months += 1
        payment_remaining = total_min_payment
        
        # Calculate interest and apply minimum payments
        for debt_name, debt in debts_copy.items():
            if debt['balance'] > 0:
                # Calculate interest for this month
                monthly_interest = debt['balance'] * (debt['interest_rate'] / 100 / 12)
                total_interest += monthly_interest
                
                # Add interest to balance
                debt['balance'] += monthly_interest
                
                # Apply minimum payment
                payment = min(debt['min_payment'], debt['balance'])
                debt['balance'] -= payment
                payment_remaining -= payment
        
        # If using a debt reduction strategy and there's payment remaining, apply it
        if payment_strategy != 'minimum' and payment_remaining > 0:
            # Sort debts according to strategy
            if payment_strategy == 'avalanche':
                # Highest interest rate first
                sorted_debts = sorted(debts_copy.items(), key=lambda x: (-x[1]['interest_rate'], x[1]['balance']))
            elif payment_strategy == 'snowball':
                # Lowest balance first
                sorted_debts = sorted(debts_copy.items(), key=lambda x: (x[1]['balance'], -x[1]['interest_rate']))
            
            # Apply remaining payment to the first debt with a balance
            for debt_name, debt in sorted_debts:
                if debt['balance'] > 0:
                    payment = min(payment_remaining, debt['balance'])
                    debt['balance'] -= payment
                    payment_remaining -= payment
                    
                    if payment_remaining <= 0:
                        break
        
        # Recalculate remaining debt
        remaining_debt = sum(debt['balance'] for debt in debts_copy.values())
    
    return months, total_interest

# Function to perform retirement impact assessment
def perform_retirement_impact_assessment():
    # Sample retirement scenarios
    retirement_scenarios = {
        'Scenario 1': {
            'current_age': 35,
            'retirement_age': 65,
            'current_savings': 50000,
            'annual_contribution': 6000,
            'expected_return_pct': 7.0,
            'inflation_pct': 2.5,
            'current_income': 75000,
            'income_replacement_pct': 80,
            'social_security_monthly': 2000,
            'life_expectancy': 85
        },
        'Scenario 2': {
            'current_age': 45,
            'retirement_age': 67,
            'current_savings': 150000,
            'annual_contribution': 12000,
            'expected_return_pct': 6.5,
            'inflation_pct': 2.5,
            'current_income': 90000,
            'income_replacement_pct': 75,
            'social_security_monthly': 2400,
            'life_expectancy': 85
        },
        'Scenario 3': {
            'current_age': 28,
            'retirement_age': 60,
            'current_savings': 30000,
            'annual_contribution': 5000,
            'expected_return_pct': 7.5,
            'inflation_pct': 2.5,
            'current_income': 65000,
            'income_replacement_pct': 85,
            'social_security_monthly': 1800,
            'life_expectancy': 90
        }
    }
    
    # Save retirement scenarios to JSON
    with open('data/financial_planning/retirement_scenarios.json', 'w') as f:
        json.dump(retirement_scenarios, f, indent=4)
    
    # Loan impact scenarios (additional loans)
    loan_impact_scenarios = {
        'No Additional Loan': {'amount': 0, 'term_years': 0, 'interest_rate': 0.0, 'monthly_payment': 0},
        'Small Loan': {'amount': 10000, 'term_years': 3, 'interest_rate': 7.5, 'monthly_payment': 311},
        'Medium Loan': {'amount': 25000, 'term_years': 5, 'interest_rate': 6.9, 'monthly_payment': 494},
        'Large Loan': {'amount': 50000, 'term_years': 10, 'interest_rate': 6.5, 'monthly_payment': 568}
    }
    
    # Save loan impact scenarios to JSON
    with open('data/financial_planning/loan_impact_scenarios.json', 'w') as f:
        json.dump(loan_impact_scenarios, f, indent=4)
    
    # Analyze each retirement scenario with each loan impact
    results = {}
    
    for scenario_name, scenario in retirement_scenarios.items():
        scenario_results = {}
        
        # Calculate baseline retirement projection
        baseline_projection = calculate_retirement_projection(scenario)
        scenario_results['baseline'] = baseline_projection
        
        # Calculate impact of each loan scenario
        for loan_name, loan in loan_impact_scenarios.items():
            if loan_name == 'No Additional Loan':
                continue  # Skip baseline scenario
            
            # Create modified scenario with loan impact
            modified_scenario = scenario.copy()
            
            # Reduce annual contribution by loan payment amount for the loan term
            modified_scenario['loan_payment'] = loan['monthly_payment'] * 12
            modified_scenario['loan_term_years'] = loan['term_years']
            
            # Calculate projection with loan impact
            loan_projection = calculate_retirement_projection(modified_scenario, loan)
            scenario_results[loan_name] = loan_projection
        
        results[scenario_name] = scenario_results
    
    # Save analysis results to JSON
    with open('data/financial_planning/retirement_impact_analysis.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    # Create visualizations
    for scenario_name, scenario_results in results.items():
        # Comparison of retirement savings
        plt.figure(figsize=(12, 6))
        
        # Plot retirement savings over time for each loan scenario
        for loan_name, projection in scenario_results.items():
            years = list(range(len(projec
(Content truncated due to size limit. Use line ranges to read in chunks)