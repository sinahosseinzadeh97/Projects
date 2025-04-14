"""
Competitive Analysis Module for Loan Prediction System
Implements market comparison, industry benchmarking,
and alternative lender recommendations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

# Create directories if they don't exist
os.makedirs('data/competitive', exist_ok=True)
os.makedirs('static/img/competitive', exist_ok=True)

# Sample market data for different lenders (in a real implementation, this would be fetched from an API)
lender_data = {
    'Traditional Banks': {
        'average_interest_rate': 7.2,
        'average_loan_amount': 22500,
        'approval_rate': 65.3,
        'processing_time_days': 14,
        'min_credit_score': 680,
        'early_repayment_penalty': True,
        'customer_satisfaction': 3.6
    },
    'Credit Unions': {
        'average_interest_rate': 6.5,
        'average_loan_amount': 18200,
        'approval_rate': 72.1,
        'processing_time_days': 10,
        'min_credit_score': 650,
        'early_repayment_penalty': False,
        'customer_satisfaction': 4.2
    },
    'Online Lenders': {
        'average_interest_rate': 8.3,
        'average_loan_amount': 15800,
        'approval_rate': 78.5,
        'processing_time_days': 3,
        'min_credit_score': 620,
        'early_repayment_penalty': False,
        'customer_satisfaction': 3.9
    },
    'Peer-to-Peer': {
        'average_interest_rate': 9.1,
        'average_loan_amount': 12500,
        'approval_rate': 82.3,
        'processing_time_days': 5,
        'min_credit_score': 600,
        'early_repayment_penalty': False,
        'customer_satisfaction': 4.0
    },
    'Our Platform': {
        'average_interest_rate': 6.8,
        'average_loan_amount': 17500,
        'approval_rate': 75.2,
        'processing_time_days': 2,
        'min_credit_score': 640,
        'early_repayment_penalty': False,
        'customer_satisfaction': 4.5
    }
}

# Save lender data to JSON file
with open('data/competitive/lender_market_data.json', 'w') as f:
    json.dump(lender_data, f, indent=4)

# Sample industry benchmark data by loan type
industry_benchmarks = {
    'Personal Loans': {
        'average_interest_rate': 7.5,
        'average_loan_amount': 16500,
        'average_term_months': 48,
        'approval_rate': 72.0,
        'default_rate': 3.8
    },
    'Debt Consolidation': {
        'average_interest_rate': 6.8,
        'average_loan_amount': 21200,
        'average_term_months': 60,
        'approval_rate': 68.5,
        'default_rate': 4.2
    },
    'Home Improvement': {
        'average_interest_rate': 6.2,
        'average_loan_amount': 25800,
        'average_term_months': 72,
        'approval_rate': 75.3,
        'default_rate': 2.9
    },
    'Medical Expenses': {
        'average_interest_rate': 8.1,
        'average_loan_amount': 12300,
        'average_term_months': 36,
        'approval_rate': 70.8,
        'default_rate': 4.5
    },
    'Education': {
        'average_interest_rate': 5.9,
        'average_loan_amount': 18700,
        'average_term_months': 84,
        'approval_rate': 78.2,
        'default_rate': 2.5
    }
}

# Save industry benchmark data to JSON file
with open('data/competitive/industry_benchmarks.json', 'w') as f:
    json.dump(industry_benchmarks, f, indent=4)

# Function to create market comparison visualizations
def create_market_comparison_visualizations():
    # Convert lender data to DataFrame for visualization
    lenders = []
    metrics = []
    values = []
    
    for lender, data in lender_data.items():
        for metric, value in data.items():
            if isinstance(value, (int, float)):  # Skip boolean values
                lenders.append(lender)
                metrics.append(metric)
                values.append(value)
    
    df = pd.DataFrame({
        'Lender': lenders,
        'Metric': metrics,
        'Value': values
    })
    
    # Create visualizations for each metric
    metrics_list = df['Metric'].unique()
    
    for metric in metrics_list:
        plt.figure(figsize=(12, 6))
        metric_data = df[df['Metric'] == metric]
        
        # Sort by value
        metric_data = metric_data.sort_values('Value')
        
        # Create bar chart
        bars = sns.barplot(x='Lender', y='Value', data=metric_data, palette='viridis')
        
        # Highlight our platform
        for i, bar in enumerate(bars.patches):
            if metric_data.iloc[i]['Lender'] == 'Our Platform':
                bar.set_color('red')
        
        plt.title(f'{metric.replace("_", " ").title()} Comparison')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'static/img/competitive/market_comparison_{metric}.png')
        plt.close()
    
    # Create radar chart for overall comparison
    # First, normalize the data for radar chart
    metrics_to_plot = ['average_interest_rate', 'approval_rate', 'processing_time_days', 'customer_satisfaction']
    
    # Determine if higher is better for each metric
    higher_is_better = {
        'average_interest_rate': False,  # Lower interest rate is better
        'approval_rate': True,           # Higher approval rate is better
        'processing_time_days': False,   # Lower processing time is better
        'customer_satisfaction': True    # Higher satisfaction is better
    }
    
    # Normalize data to 0-1 scale
    normalized_data = {}
    for metric in metrics_to_plot:
        metric_values = [data[metric] for lender, data in lender_data.items()]
        min_val = min(metric_values)
        max_val = max(metric_values)
        
        for lender, data in lender_data.items():
            if lender not in normalized_data:
                normalized_data[lender] = {}
            
            # Normalize and invert if lower is better
            if higher_is_better[metric]:
                normalized_data[lender][metric] = (data[metric] - min_val) / (max_val - min_val)
            else:
                normalized_data[lender][metric] = 1 - (data[metric] - min_val) / (max_val - min_val)
    
    # Create radar chart
    plt.figure(figsize=(10, 10))
    
    # Set up the radar chart
    angles = np.linspace(0, 2*np.pi, len(metrics_to_plot), endpoint=False).tolist()
    angles += angles[:1]  # Close the loop
    
    ax = plt.subplot(111, polar=True)
    
    # Add metric labels
    plt.xticks(angles[:-1], [m.replace('_', ' ').title() for m in metrics_to_plot])
    
    # Plot each lender
    for lender, data in normalized_data.items():
        values = [data[metric] for metric in metrics_to_plot]
        values += values[:1]  # Close the loop
        
        # Plot the lender data
        ax.plot(angles, values, linewidth=2, label=lender)
        ax.fill(angles, values, alpha=0.1)
    
    plt.title('Lender Comparison Radar Chart')
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.savefig('static/img/competitive/lender_radar_comparison.png')
    plt.close()

# Function to create industry benchmark visualizations
def create_industry_benchmark_visualizations():
    # Convert industry benchmark data to DataFrame for visualization
    loan_types = []
    metrics = []
    values = []
    
    for loan_type, data in industry_benchmarks.items():
        for metric, value in data.items():
            loan_types.append(loan_type)
            metrics.append(metric)
            values.append(value)
    
    df = pd.DataFrame({
        'Loan Type': loan_types,
        'Metric': metrics,
        'Value': values
    })
    
    # Create visualizations for each metric
    metrics_list = df['Metric'].unique()
    
    for metric in metrics_list:
        plt.figure(figsize=(12, 6))
        metric_data = df[df['Metric'] == metric]
        
        # Sort by value
        metric_data = metric_data.sort_values('Value')
        
        # Create bar chart
        sns.barplot(x='Loan Type', y='Value', data=metric_data, palette='viridis')
        
        plt.title(f'{metric.replace("_", " ").title()} by Loan Type')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'static/img/competitive/benchmark_{metric}.png')
        plt.close()
    
    # Create heatmap of all metrics by loan type
    pivot_df = df.pivot(index='Loan Type', columns='Metric', values='Value')
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_df, annot=True, cmap='YlGnBu', fmt='.1f')
    plt.title('Industry Benchmarks by Loan Type')
    plt.tight_layout()
    plt.savefig('static/img/competitive/benchmark_heatmap.png')
    plt.close()

# Function to create alternative lender recommendations
def create_alternative_lender_recommendations():
    # Sample alternative lenders with their characteristics
    alternative_lenders = {
        'QuickLoan': {
            'specialties': ['Personal Loans', 'Debt Consolidation'],
            'interest_rate_range': '6.5% - 12.8%',
            'loan_amount_range': '$5,000 - $35,000',
            'min_credit_score': 640,
            'pros': ['Fast approval (24 hours)', 'No early repayment fees', 'Flexible terms'],
            'cons': ['Higher rates for lower credit scores', 'Limited loan types']
        },
        'CreditUnion Plus': {
            'specialties': ['Home Improvement', 'Auto Loans', 'Personal Loans'],
            'interest_rate_range': '5.2% - 9.5%',
            'loan_amount_range': '$2,500 - $50,000',
            'min_credit_score': 660,
            'pros': ['Lower interest rates', 'Personalized service', 'Member benefits'],
            'cons': ['Membership required', 'Longer approval process', 'Branch visit may be required']
        },
        'PeerFund': {
            'specialties': ['Business Loans', 'Education', 'Medical Expenses'],
            'interest_rate_range': '7.8% - 15.2%',
            'loan_amount_range': '$1,000 - $40,000',
            'min_credit_score': 600,
            'pros': ['Accessible to lower credit scores', 'Unique loan purposes', 'Community funded'],
            'cons': ['Higher average rates', 'Funding may take longer', 'Additional platform fees']
        },
        'EasyFinance': {
            'specialties': ['Debt Consolidation', 'Home Improvement', 'Major Purchases'],
            'interest_rate_range': '6.9% - 11.5%',
            'loan_amount_range': '$10,000 - $75,000',
            'min_credit_score': 680,
            'pros': ['Higher loan amounts', 'Rate discounts for autopay', 'No origination fees'],
            'cons': ['Stricter credit requirements', 'Limited availability in some states']
        },
        'MobileLender': {
            'specialties': ['Personal Loans', 'Emergency Expenses', 'Short-term Loans'],
            'interest_rate_range': '8.5% - 17.9%',
            'loan_amount_range': '$500 - $15,000',
            'min_credit_score': 580,
            'pros': ['Mobile-first application', 'Same-day funding available', 'Accepts lower credit scores'],
            'cons': ['Higher interest rates', 'Lower maximum loan amounts', 'Shorter terms']
        }
    }
    
    # Save alternative lender data to JSON file
    with open('data/competitive/alternative_lenders.json', 'w') as f:
        json.dump(alternative_lenders, f, indent=4)
    
    # Create visualization of lender specialties
    specialties = {}
    for lender, data in alternative_lenders.items():
        for specialty in data['specialties']:
            if specialty not in specialties:
                specialties[specialty] = []
            specialties[specialty].append(lender)
    
    # Convert to DataFrame for visualization
    specialty_df = []
    for specialty, lenders in specialties.items():
        for lender in lenders:
            specialty_df.append({
                'Specialty': specialty,
                'Lender': lender
            })
    
    specialty_df = pd.DataFrame(specialty_df)
    
    # Create grouped bar chart
    plt.figure(figsize=(12, 8))
    sns.countplot(x='Specialty', hue='Lender', data=specialty_df, palette='viridis')
    plt.title('Lender Specialties')
    plt.xticks(rotation=45)
    plt.legend(title='Lender')
    plt.tight_layout()
    plt.savefig('static/img/competitive/lender_specialties.png')
    plt.close()
    
    # Create visualization of interest rate ranges
    plt.figure(figsize=(12, 6))
    
    # Extract min and max rates
    min_rates = []
    max_rates = []
    lender_names = []
    
    for lender, data in alternative_lenders.items():
        rate_range = data['interest_rate_range']
        min_rate, max_rate = rate_range.replace('%', '').split(' - ')
        min_rates.append(float(min_rate))
        max_rates.append(float(max_rate))
        lender_names.append(lender)
    
    # Sort by minimum rate
    sorted_indices = np.argsort(min_rates)
    min_rates = [min_rates[i] for i in sorted_indices]
    max_rates = [max_rates[i] for i in sorted_indices]
    lender_names = [lender_names[i] for i in sorted_indices]
    
    # Create horizontal bar chart
    y_pos = np.arange(len(lender_names))
    
    plt.barh(y_pos, np.array(max_rates) - np.array(min_rates), left=min_rates, height=0.5, color='skyblue')
    
    # Add lender names and rate labels
    plt.yticks(y_pos, lender_names)
    
    for i, (min_rate, max_rate) in enumerate(zip(min_rates, max_rates)):
        plt.text(min_rate - 0.5, i, f'{min_rate}%', va='center', ha='right')
        plt.text(max_rate + 0.5, i, f'{max_rate}%', va='center', ha='left')
    
    plt.xlabel('Interest Rate (%)')
    plt.title('Interest Rate Ranges by Lender')
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig('static/img/competitive/interest_rate_ranges.png')
    plt.close()

# Execute all functions to generate the visualizations and data
if __name__ == "__main__":
    print("Generating competitive analysis visualizations and data...")
    create_market_comparison_visualizations()
    create_industry_benchmark_visualizations()
    create_alternative_lender_recommendations()
    print("Competitive analysis implementation complete!")
