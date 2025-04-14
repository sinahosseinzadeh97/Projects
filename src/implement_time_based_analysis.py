"""
Time-Based Analysis Module for Loan Prediction System
Implements seasonal trend detection, loan performance forecasting,
and repayment timeline projections with visualization.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
import os
import json
from datetime import datetime, timedelta

# Create directories if they don't exist
os.makedirs('data/time_based', exist_ok=True)
os.makedirs('static/img/time_based', exist_ok=True)

# Generate sample time series data for loan performance
def generate_sample_time_series_data():
    # Create date range for the past 3 years with monthly data
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2025, 3, 1)
    date_range = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    # Generate sample data with seasonal patterns
    np.random.seed(42)  # For reproducibility
    
    # Default rates with seasonal pattern (higher in summer and winter)
    base_default_rate = 3.5
    seasonal_component = 0.8 * np.sin(np.linspace(0, 6*np.pi, len(date_range)))
    trend_component = np.linspace(0, -0.5, len(date_range))  # Slight downward trend
    noise = np.random.normal(0, 0.2, len(date_range))
    default_rates = base_default_rate + seasonal_component + trend_component + noise
    default_rates = np.maximum(default_rates, 1.0)  # Ensure minimum value
    
    # Approval rates (inverse relationship with default rates)
    base_approval_rate = 72.0
    approval_rates = base_approval_rate - seasonal_component * 2 - trend_component * 3 + np.random.normal(0, 1.0, len(date_range))
    approval_rates = np.clip(approval_rates, 65.0, 80.0)  # Ensure values in reasonable range
    
    # Average interest rates (slight seasonal pattern)
    base_interest_rate = 6.5
    interest_rates = base_interest_rate + 0.3 * seasonal_component + np.linspace(0, 0.8, len(date_range)) + np.random.normal(0, 0.1, len(date_range))
    
    # Average loan amount (increasing trend with seasonality)
    base_loan_amount = 15000
    loan_amounts = base_loan_amount + 300 * seasonal_component + np.linspace(0, 3000, len(date_range)) + np.random.normal(0, 200, len(date_range))
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': date_range,
        'default_rate': default_rates,
        'approval_rate': approval_rates,
        'interest_rate': interest_rates,
        'loan_amount': loan_amounts
    })
    
    # Save to CSV
    df.to_csv('data/time_based/loan_performance_time_series.csv', index=False)
    
    return df

# Function to perform seasonal decomposition
def perform_seasonal_decomposition(df):
    metrics = ['default_rate', 'approval_rate', 'interest_rate', 'loan_amount']
    results = {}
    
    for metric in metrics:
        # Set the date as index
        ts_data = df.set_index('date')[metric]
        
        # Perform seasonal decomposition
        decomposition = seasonal_decompose(ts_data, model='additive', period=12)
        
        # Store results
        results[metric] = {
            'trend': decomposition.trend.dropna().tolist(),
            'seasonal': decomposition.seasonal.dropna().tolist(),
            'residual': decomposition.resid.dropna().tolist()
        }
        
        # Create visualization
        plt.figure(figsize=(15, 12))
        
        plt.subplot(411)
        plt.plot(ts_data, label='Original')
        plt.legend(loc='best')
        plt.title(f'Seasonal Decomposition of {metric.replace("_", " ").title()}')
        
        plt.subplot(412)
        plt.plot(decomposition.trend, label='Trend')
        plt.legend(loc='best')
        
        plt.subplot(413)
        plt.plot(decomposition.seasonal, label='Seasonality')
        plt.legend(loc='best')
        
        plt.subplot(414)
        plt.plot(decomposition.resid, label='Residuals')
        plt.legend(loc='best')
        
        plt.tight_layout()
        plt.savefig(f'static/img/time_based/seasonal_decomposition_{metric}.png')
        plt.close()
    
    # Save decomposition results to JSON
    with open('data/time_based/seasonal_decomposition_results.json', 'w') as f:
        json.dump(results, f, indent=4)

# Function to create loan performance forecasts
def create_loan_performance_forecasts(df):
    # Forecast for the next 12 months
    forecast_periods = 12
    metrics = ['default_rate', 'approval_rate', 'interest_rate', 'loan_amount']
    forecast_results = {}
    
    for metric in metrics:
        # Set the date as index
        ts_data = df.set_index('date')[metric]
        
        # Fit ARIMA model
        # In a real implementation, we would perform proper order selection
        # For this example, we'll use a simple (1,1,1) model
        model = ARIMA(ts_data, order=(1,1,1))
        model_fit = model.fit()
        
        # Make forecast
        forecast = model_fit.forecast(steps=forecast_periods)
        
        # Create date range for forecast
        last_date = df['date'].max()
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=forecast_periods, freq='MS')
        
        # Store forecast results
        forecast_results[metric] = {
            'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
            'values': forecast.tolist()
        }
        
        # Create visualization
        plt.figure(figsize=(12, 6))
        
        # Plot historical data
        plt.plot(ts_data.index, ts_data.values, label='Historical')
        
        # Plot forecast
        plt.plot(forecast_dates, forecast, label='Forecast', color='red')
        
        # Add confidence intervals (simplified for this example)
        std_error = model_fit.params[0] * 2  # Simplified error calculation
        plt.fill_between(forecast_dates, 
                         forecast - 1.96 * std_error,
                         forecast + 1.96 * std_error,
                         color='red', alpha=0.2, label='95% Confidence Interval')
        
        plt.title(f'{metric.replace("_", " ").title()} Forecast')
        plt.xlabel('Date')
        plt.ylabel(metric.replace("_", " ").title())
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'static/img/time_based/forecast_{metric}.png')
        plt.close()
    
    # Save forecast results to JSON
    with open('data/time_based/forecast_results.json', 'w') as f:
        json.dump(forecast_results, f, indent=4)

# Function to create repayment timeline projections
def create_repayment_timeline_projections():
    # Sample loan parameters
    loan_amounts = [10000, 20000, 30000]
    interest_rates = [5.0, 7.5, 10.0]
    terms = [36, 60, 120]  # months
    
    results = {}
    
    for amount in loan_amounts:
        for rate in interest_rates:
            for term in terms:
                # Calculate monthly payment
                monthly_rate = rate / 100 / 12
                monthly_payment = amount * monthly_rate * (1 + monthly_rate) ** term / ((1 + monthly_rate) ** term - 1)
                
                # Generate amortization schedule
                remaining_balance = amount
                monthly_payments = []
                principal_payments = []
                interest_payments = []
                remaining_balances = []
                
                for month in range(1, term + 1):
                    interest_payment = remaining_balance * monthly_rate
                    principal_payment = monthly_payment - interest_payment
                    remaining_balance -= principal_payment
                    
                    monthly_payments.append(monthly_payment)
                    principal_payments.append(principal_payment)
                    interest_payments.append(interest_payment)
                    remaining_balances.append(remaining_balance)
                
                # Store results
                key = f"amount_{amount}_rate_{rate}_term_{term}"
                results[key] = {
                    'loan_amount': amount,
                    'interest_rate': rate,
                    'term': term,
                    'monthly_payment': monthly_payment,
                    'total_payment': monthly_payment * term,
                    'total_interest': (monthly_payment * term) - amount,
                    'amortization': {
                        'principal_payments': principal_payments[::6],  # Store every 6th month to reduce data size
                        'interest_payments': interest_payments[::6],
                        'remaining_balances': remaining_balances[::6]
                    }
                }
                
                # Create visualization for selected combinations
                if (amount == 20000 and rate == 7.5) or (amount == 30000 and rate == 5.0) or (amount == 10000 and rate == 10.0):
                    plt.figure(figsize=(12, 8))
                    
                    # Plot remaining balance over time
                    plt.subplot(211)
                    plt.plot(range(1, term + 1), remaining_balances)
                    plt.title(f'Loan Repayment Timeline: ${amount}, {rate}%, {term} months')
                    plt.ylabel('Remaining Balance ($)')
                    plt.grid(True, alpha=0.3)
                    
                    # Plot principal vs interest payments
                    plt.subplot(212)
                    months = range(1, term + 1)
                    plt.bar(months, principal_payments, label='Principal', alpha=0.7)
                    plt.bar(months, interest_payments, bottom=principal_payments, label='Interest', alpha=0.7)
                    plt.xlabel('Month')
                    plt.ylabel('Payment Amount ($)')
                    plt.legend()
                    plt.grid(True, alpha=0.3)
                    
                    plt.tight_layout()
                    plt.savefig(f'static/img/time_based/repayment_timeline_{amount}_{rate}_{term}.png')
                    plt.close()
    
    # Save repayment timeline results to JSON
    with open('data/time_based/repayment_timeline_results.json', 'w') as f:
        json.dump(results, f, indent=4)

# Function to create a visualization of seasonal loan trends
def create_seasonal_loan_trends_visualization(df):
    # Group by month to see seasonal patterns
    df['month'] = df['date'].dt.month
    monthly_averages = df.groupby('month').agg({
        'default_rate': 'mean',
        'approval_rate': 'mean',
        'interest_rate': 'mean',
        'loan_amount': 'mean'
    }).reset_index()
    
    # Add month names
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_averages['month_name'] = monthly_averages['month'].apply(lambda x: month_names[x-1])
    
    # Create visualization
    plt.figure(figsize=(15, 10))
    
    metrics = ['default_rate', 'approval_rate', 'interest_rate', 'loan_amount']
    for i, metric in enumerate(metrics):
        plt.subplot(2, 2, i+1)
        sns.barplot(x='month_name', y=metric, data=monthly_averages)
        plt.title(f'Average {metric.replace("_", " ").title()} by Month')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('static/img/time_based/seasonal_loan_trends.png')
    plt.close()
    
    # Save seasonal trends to JSON
    seasonal_trends = monthly_averages.to_dict(orient='records')
    with open('data/time_based/seasonal_trends.json', 'w') as f:
        json.dump(seasonal_trends, f, indent=4)

# Execute all functions to generate the visualizations and data
if __name__ == "__main__":
    print("Generating time-based analysis visualizations and data...")
    df = generate_sample_time_series_data()
    perform_seasonal_decomposition(df)
    create_loan_performance_forecasts(df)
    create_repayment_timeline_projections()
    create_seasonal_loan_trends_visualization(df)
    print("Time-based analysis implementation complete!")
