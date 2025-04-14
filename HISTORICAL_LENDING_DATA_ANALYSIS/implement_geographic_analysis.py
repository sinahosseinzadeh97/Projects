"""
Geographic Analysis Module for Loan Prediction System
Implements location-based risk assessment, regional economic indicators analysis,
and visualization of loan performance by geographic region.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
import os
import json

# Create directories if they don't exist
os.makedirs('data/geographic', exist_ok=True)
os.makedirs('static/img/geographic', exist_ok=True)

# Sample regional economic data (in a real implementation, this would be fetched from an API)
regional_economic_data = {
    'Northeast': {
        'unemployment_rate': 4.2,
        'median_income': 72500,
        'housing_price_index': 285.3,
        'gdp_growth': 2.1,
        'default_rate': 3.8
    },
    'Midwest': {
        'unemployment_rate': 3.8,
        'median_income': 65200,
        'housing_price_index': 210.5,
        'gdp_growth': 1.9,
        'default_rate': 3.2
    },
    'South': {
        'unemployment_rate': 4.5,
        'median_income': 61800,
        'housing_price_index': 195.7,
        'gdp_growth': 2.3,
        'default_rate': 4.1
    },
    'West': {
        'unemployment_rate': 4.0,
        'median_income': 78300,
        'housing_price_index': 320.1,
        'gdp_growth': 2.5,
        'default_rate': 3.5
    }
}

# Save regional economic data to JSON file
with open('data/geographic/regional_economic_data.json', 'w') as f:
    json.dump(regional_economic_data, f, indent=4)

# Sample state-level default rates (in a real implementation, this would be fetched from an API)
state_default_rates = {
    'AL': 4.2, 'AK': 3.8, 'AZ': 4.5, 'AR': 4.0, 'CA': 3.9, 'CO': 3.2, 'CT': 3.5, 'DE': 3.7,
    'FL': 4.3, 'GA': 4.1, 'HI': 3.0, 'ID': 3.4, 'IL': 3.8, 'IN': 3.6, 'IA': 3.0, 'KS': 3.3,
    'KY': 4.0, 'LA': 4.5, 'ME': 3.4, 'MD': 3.6, 'MA': 3.2, 'MI': 3.7, 'MN': 3.1, 'MS': 4.6,
    'MO': 3.5, 'MT': 3.3, 'NE': 3.0, 'NV': 4.4, 'NH': 3.1, 'NJ': 3.5, 'NM': 4.3, 'NY': 3.7,
    'NC': 3.9, 'ND': 2.9, 'OH': 3.6, 'OK': 3.8, 'OR': 3.5, 'PA': 3.4, 'RI': 3.6, 'SC': 4.0,
    'SD': 3.1, 'TN': 4.0, 'TX': 3.8, 'UT': 3.2, 'VT': 3.0, 'VA': 3.5, 'WA': 3.4, 'WV': 4.2,
    'WI': 3.3, 'WY': 3.4
}

# Save state default rates to JSON file
with open('data/geographic/state_default_rates.json', 'w') as f:
    json.dump(state_default_rates, f, indent=4)

# Function to create a heatmap of default rates by state
def create_state_default_rate_heatmap():
    # Convert state default rates to DataFrame
    df = pd.DataFrame(list(state_default_rates.items()), columns=['State', 'Default_Rate'])
    
    # Create a pivot table for the heatmap (in a real implementation, this would use actual geographic coordinates)
    # For this example, we'll create a simplified 10x5 grid to represent the US
    state_grid = {
        'WA': (0, 0), 'MT': (0, 1), 'ND': (0, 2), 'MN': (0, 3), 'WI': (0, 4), 'MI': (0, 5), 'ME': (0, 6), 'VT': (0, 7), 'NH': (0, 8), 'MA': (0, 9),
        'OR': (1, 0), 'ID': (1, 1), 'SD': (1, 2), 'IA': (1, 3), 'IL': (1, 4), 'IN': (1, 5), 'OH': (1, 6), 'PA': (1, 7), 'NJ': (1, 8), 'CT': (1, 9),
        'CA': (2, 0), 'NV': (2, 1), 'WY': (2, 2), 'NE': (2, 3), 'MO': (2, 4), 'KY': (2, 5), 'WV': (2, 6), 'VA': (2, 7), 'MD': (2, 8), 'DE': (2, 9),
        'AZ': (3, 0), 'UT': (3, 1), 'CO': (3, 2), 'KS': (3, 3), 'AR': (3, 4), 'TN': (3, 5), 'NC': (3, 6), 'SC': (3, 7), 'DC': (3, 8), 'RI': (3, 9),
        'NM': (4, 0), 'OK': (4, 1), 'TX': (4, 2), 'LA': (4, 3), 'MS': (4, 4), 'AL': (4, 5), 'GA': (4, 6), 'FL': (4, 7), 'HI': (4, 8), 'AK': (4, 9)
    }
    
    # Create a grid for the heatmap
    grid = np.zeros((5, 10))
    for state, rate in state_default_rates.items():
        if state in state_grid:
            row, col = state_grid[state]
            grid[row, col] = rate
    
    # Create the heatmap
    plt.figure(figsize=(15, 8))
    sns.heatmap(grid, annot=True, cmap='YlOrRd', fmt='.1f', cbar_kws={'label': 'Default Rate (%)'})
    plt.title('Loan Default Rates by State (Simplified Geographic Representation)')
    plt.xlabel('East →')
    plt.ylabel('North ↑')
    plt.tight_layout()
    plt.savefig('static/img/geographic/state_default_rates.png')
    plt.close()

# Function to create regional economic indicators comparison
def create_regional_economic_comparison():
    # Convert regional data to DataFrame
    regions = []
    metrics = []
    values = []
    
    for region, data in regional_economic_data.items():
        for metric, value in data.items():
            regions.append(region)
            metrics.append(metric)
            values.append(value)
    
    df = pd.DataFrame({
        'Region': regions,
        'Metric': metrics,
        'Value': values
    })
    
    # Create a grouped bar chart
    plt.figure(figsize=(15, 10))
    
    # Plot each metric separately
    metrics_list = df['Metric'].unique()
    for i, metric in enumerate(metrics_list):
        plt.subplot(3, 2, i+1)
        metric_data = df[df['Metric'] == metric]
        sns.barplot(x='Region', y='Value', data=metric_data)
        plt.title(f'{metric.replace("_", " ").title()}')
        plt.xticks(rotation=45)
        plt.tight_layout()
    
    plt.savefig('static/img/geographic/regional_economic_indicators.png')
    plt.close()

# Function to create loan performance by region visualization
def create_loan_performance_by_region():
    # Sample loan performance data by region (in a real implementation, this would be calculated from actual loan data)
    loan_performance = {
        'Northeast': {
            'approval_rate': 72.5,
            'average_interest_rate': 6.8,
            'average_loan_amount': 18500,
            'default_rate': 3.8,
            'early_payoff_rate': 12.3
        },
        'Midwest': {
            'approval_rate': 75.2,
            'average_interest_rate': 6.5,
            'average_loan_amount': 16200,
            'default_rate': 3.2,
            'early_payoff_rate': 10.8
        },
        'South': {
            'approval_rate': 68.7,
            'average_interest_rate': 7.2,
            'average_loan_amount': 15800,
            'default_rate': 4.1,
            'early_payoff_rate': 9.5
        },
        'West': {
            'approval_rate': 70.3,
            'average_interest_rate': 7.0,
            'average_loan_amount': 19300,
            'default_rate': 3.5,
            'early_payoff_rate': 11.7
        }
    }
    
    # Save loan performance data to JSON file
    with open('data/geographic/loan_performance_by_region.json', 'w') as f:
        json.dump(loan_performance, f, indent=4)
    
    # Convert to DataFrame for visualization
    regions = []
    metrics = []
    values = []
    
    for region, data in loan_performance.items():
        for metric, value in data.items():
            regions.append(region)
            metrics.append(metric)
            values.append(value)
    
    df = pd.DataFrame({
        'Region': regions,
        'Metric': metrics,
        'Value': values
    })
    
    # Create visualizations for each metric
    metrics_list = df['Metric'].unique()
    plt.figure(figsize=(15, 12))
    
    for i, metric in enumerate(metrics_list):
        plt.subplot(3, 2, i+1)
        metric_data = df[df['Metric'] == metric]
        sns.barplot(x='Region', y='Value', data=metric_data, palette='viridis')
        plt.title(f'{metric.replace("_", " ").title()} by Region')
        plt.xticks(rotation=45)
        plt.tight_layout()
    
    plt.savefig('static/img/geographic/loan_performance_by_region.png')
    plt.close()

# Function to create a risk assessment model based on location
def create_location_based_risk_model():
    # In a real implementation, this would be a machine learning model trained on geographic features
    # For this example, we'll create a simple risk scoring system based on regional economic indicators
    
    # Calculate risk scores for each region
    risk_scores = {}
    for region, data in regional_economic_data.items():
        # Simple weighted formula for risk score (lower is better)
        risk_score = (
            data['unemployment_rate'] * 0.3 +
            (100000 / data['median_income']) * 0.25 +
            (data['housing_price_index'] / 100) * 0.15 -
            data['gdp_growth'] * 0.3
        )
        risk_scores[region] = risk_score
    
    # Normalize scores to 0-100 scale (higher is riskier)
    min_score = min(risk_scores.values())
    max_score = max(risk_scores.values())
    normalized_scores = {
        region: ((score - min_score) / (max_score - min_score)) * 100
        for region, score in risk_scores.items()
    }
    
    # Save risk scores to JSON file
    with open('data/geographic/regional_risk_scores.json', 'w') as f:
        json.dump(normalized_scores, f, indent=4)
    
    # Create visualization of risk scores
    plt.figure(figsize=(10, 6))
    regions = list(normalized_scores.keys())
    scores = list(normalized_scores.values())
    
    # Create color map based on risk score
    colors = ['green', 'yellowgreen', 'orange', 'red']
    risk_colors = []
    for score in scores:
        if score < 25:
            risk_colors.append(colors[0])
        elif score < 50:
            risk_colors.append(colors[1])
        elif score < 75:
            risk_colors.append(colors[2])
        else:
            risk_colors.append(colors[3])
    
    bars = plt.bar(regions, scores, color=risk_colors)
    plt.title('Regional Risk Assessment Scores')
    plt.xlabel('Region')
    plt.ylabel('Risk Score (0-100, higher is riskier)')
    plt.ylim(0, 100)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{height:.1f}',
                 ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('static/img/geographic/regional_risk_scores.png')
    plt.close()

# Execute all functions to generate the visualizations and data
if __name__ == "__main__":
    print("Generating geographic analysis visualizations and data...")
    create_state_default_rate_heatmap()
    create_regional_economic_comparison()
    create_loan_performance_by_region()
    create_location_based_risk_model()
    print("Geographic analysis implementation complete!")
