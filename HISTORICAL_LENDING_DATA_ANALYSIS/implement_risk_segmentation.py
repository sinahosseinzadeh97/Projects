"""
Risk Segmentation Module for Loan Prediction System
Implements detailed risk profiles, tiered risk categorization,
and custom scoring models for different borrower segments.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
import json

# Create directories if they don't exist
os.makedirs('data/risk_segmentation', exist_ok=True)
os.makedirs('static/img/risk_segmentation', exist_ok=True)

# Generate sample borrower data for risk segmentation
def generate_sample_borrower_data(n_samples=1000):
    np.random.seed(42)  # For reproducibility
    
    # Generate features
    annual_income = np.random.normal(65000, 25000, n_samples)
    credit_score = np.random.normal(680, 75, n_samples)
    debt_to_income = np.random.normal(28, 12, n_samples)
    loan_amount = np.random.normal(18000, 8000, n_samples)
    loan_term = np.random.choice([12, 24, 36, 48, 60, 72], n_samples)
    interest_rate = np.random.normal(7.5, 2.5, n_samples)
    employment_length = np.random.normal(6, 4, n_samples)
    num_credit_lines = np.random.normal(8, 4, n_samples)
    num_delinquencies = np.random.exponential(0.5, n_samples)
    
    # Ensure values are in reasonable ranges
    annual_income = np.maximum(annual_income, 15000)
    credit_score = np.clip(credit_score, 300, 850)
    debt_to_income = np.clip(debt_to_income, 0, 100)
    loan_amount = np.maximum(loan_amount, 1000)
    employment_length = np.maximum(employment_length, 0)
    num_credit_lines = np.maximum(num_credit_lines, 0).astype(int)
    num_delinquencies = np.maximum(num_delinquencies, 0).astype(int)
    
    # Create DataFrame
    df = pd.DataFrame({
        'annual_income': annual_income,
        'credit_score': credit_score,
        'debt_to_income': debt_to_income,
        'loan_amount': loan_amount,
        'loan_term': loan_term,
        'interest_rate': interest_rate,
        'employment_length': employment_length,
        'num_credit_lines': num_credit_lines,
        'num_delinquencies': num_delinquencies
    })
    
    # Generate loan status based on features (simplified model)
    # Higher credit score, income, and employment length increase chances of good standing
    # Higher debt-to-income, interest rate, and delinquencies increase default risk
    default_prob = (
        -0.5 * (df['credit_score'] - 300) / 550 +
        -0.2 * np.log1p(df['annual_income']) / np.log1p(200000) +
        0.4 * df['debt_to_income'] / 100 +
        0.2 * df['interest_rate'] / 20 +
        -0.1 * df['employment_length'] / 20 +
        0.3 * df['num_delinquencies'] / 10 +
        0.1 * np.random.normal(0, 1, n_samples)  # Random noise
    )
    
    # Normalize to 0-1 range
    default_prob = (default_prob - default_prob.min()) / (default_prob.max() - default_prob.min())
    
    # Assign loan status
    df['default_probability'] = default_prob
    df['loan_status'] = np.where(default_prob < 0.5, 'Fully Paid', 'Charged Off')
    
    # Save to CSV
    df.to_csv('data/risk_segmentation/borrower_data.csv', index=False)
    
    return df

# Function to create risk tiers
def create_risk_tiers(df):
    # Create risk score (inverse of default probability)
    df['risk_score'] = 100 * (1 - df['default_probability'])
    
    # Define risk tiers
    conditions = [
        (df['risk_score'] >= 90),
        (df['risk_score'] >= 80) & (df['risk_score'] < 90),
        (df['risk_score'] >= 70) & (df['risk_score'] < 80),
        (df['risk_score'] >= 60) & (df['risk_score'] < 70),
        (df['risk_score'] >= 50) & (df['risk_score'] < 60),
        (df['risk_score'] < 50)
    ]
    
    tier_labels = ['A+ (Excellent)', 'A (Very Good)', 'B (Good)', 'C (Fair)', 'D (Poor)', 'E (High Risk)']
    df['risk_tier'] = np.select(conditions, tier_labels, default='Unknown')
    
    # Calculate tier statistics
    tier_stats = df.groupby('risk_tier').agg({
        'default_probability': 'mean',
        'credit_score': 'mean',
        'annual_income': 'mean',
        'debt_to_income': 'mean',
        'interest_rate': 'mean',
        'loan_amount': 'mean',
        'risk_score': 'mean',
        'loan_status': lambda x: (x == 'Fully Paid').mean() * 100  # Repayment rate as percentage
    }).reset_index()
    
    # Rename columns for clarity
    tier_stats = tier_stats.rename(columns={
        'default_probability': 'avg_default_probability',
        'credit_score': 'avg_credit_score',
        'annual_income': 'avg_annual_income',
        'debt_to_income': 'avg_debt_to_income',
        'interest_rate': 'avg_interest_rate',
        'loan_amount': 'avg_loan_amount',
        'risk_score': 'avg_risk_score',
        'loan_status': 'repayment_rate_pct'
    })
    
    # Save tier statistics to JSON
    tier_stats_dict = tier_stats.to_dict(orient='records')
    with open('data/risk_segmentation/risk_tier_statistics.json', 'w') as f:
        json.dump(tier_stats_dict, f, indent=4)
    
    # Create visualization of risk tiers
    plt.figure(figsize=(12, 8))
    
    # Count plot of risk tiers
    plt.subplot(2, 2, 1)
    sns.countplot(x='risk_tier', data=df, order=tier_labels)
    plt.title('Distribution of Risk Tiers')
    plt.xticks(rotation=45)
    
    # Default probability by risk tier
    plt.subplot(2, 2, 2)
    sns.boxplot(x='risk_tier', y='default_probability', data=df, order=tier_labels)
    plt.title('Default Probability by Risk Tier')
    plt.xticks(rotation=45)
    
    # Credit score by risk tier
    plt.subplot(2, 2, 3)
    sns.boxplot(x='risk_tier', y='credit_score', data=df, order=tier_labels)
    plt.title('Credit Score by Risk Tier')
    plt.xticks(rotation=45)
    
    # Debt-to-income by risk tier
    plt.subplot(2, 2, 4)
    sns.boxplot(x='risk_tier', y='debt_to_income', data=df, order=tier_labels)
    plt.title('Debt-to-Income Ratio by Risk Tier')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('static/img/risk_segmentation/risk_tier_analysis.png')
    plt.close()
    
    # Create heatmap of tier statistics
    plt.figure(figsize=(14, 8))
    
    # Prepare data for heatmap
    heatmap_data = tier_stats.set_index('risk_tier')
    
    # Normalize data for better visualization
    scaler = StandardScaler()
    heatmap_data_scaled = pd.DataFrame(
        scaler.fit_transform(heatmap_data),
        columns=heatmap_data.columns,
        index=heatmap_data.index
    )
    
    # Create heatmap
    sns.heatmap(heatmap_data_scaled, annot=False, cmap='coolwarm', linewidths=0.5)
    plt.title('Risk Tier Characteristics (Normalized)')
    plt.tight_layout()
    plt.savefig('static/img/risk_segmentation/risk_tier_heatmap.png')
    plt.close()
    
    return df

# Function to create borrower segments using clustering
def create_borrower_segments(df):
    # Select features for clustering
    features = ['credit_score', 'annual_income', 'debt_to_income', 'employment_length', 'num_delinquencies']
    X = df[features].copy()
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Determine optimal number of clusters using elbow method
    inertia = []
    k_range = range(2, 11)
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertia.append(kmeans.inertia_)
    
    # Plot elbow method
    plt.figure(figsize=(10, 6))
    plt.plot(k_range, inertia, 'o-')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Inertia')
    plt.title('Elbow Method for Optimal k')
    plt.grid(True, alpha=0.3)
    plt.savefig('static/img/risk_segmentation/elbow_method.png')
    plt.close()
    
    # Choose k=5 for this example (in a real implementation, this would be chosen based on the elbow method)
    k = 5
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    df['segment'] = kmeans.fit_predict(X_scaled)
    
    # Calculate segment statistics
    segment_stats = df.groupby('segment').agg({
        'credit_score': 'mean',
        'annual_income': 'mean',
        'debt_to_income': 'mean',
        'employment_length': 'mean',
        'num_delinquencies': 'mean',
        'default_probability': 'mean',
        'risk_score': 'mean',
        'loan_status': lambda x: (x == 'Fully Paid').mean() * 100  # Repayment rate as percentage
    }).reset_index()
    
    # Rename segments based on characteristics
    segment_names = []
    for _, row in segment_stats.iterrows():
        if row['credit_score'] > 720 and row['annual_income'] > 80000:
            name = "Prime Borrowers"
        elif row['credit_score'] > 680 and row['annual_income'] > 60000:
            name = "Near-Prime Borrowers"
        elif row['debt_to_income'] > 40 and row['num_delinquencies'] > 1:
            name = "High-DTI Borrowers"
        elif row['employment_length'] < 3:
            name = "New Earners"
        else:
            name = "Average Borrowers"
        segment_names.append(name)
    
    # Create mapping from segment number to name
    segment_mapping = {i: name for i, name in enumerate(segment_names)}
    
    # Apply mapping to DataFrame
    df['segment_name'] = df['segment'].map(segment_mapping)
    
    # Update segment statistics with names
    segment_stats['segment_name'] = segment_names
    
    # Save segment statistics to JSON
    segment_stats_dict = segment_stats.to_dict(orient='records')
    with open('data/risk_segmentation/borrower_segment_statistics.json', 'w') as f:
        json.dump(segment_stats_dict, f, indent=4)
    
    # Create visualization of borrower segments
    plt.figure(figsize=(15, 10))
    
    # Count plot of segments
    plt.subplot(2, 3, 1)
    sns.countplot(x='segment_name', data=df)
    plt.title('Distribution of Borrower Segments')
    plt.xticks(rotation=45)
    
    # Default probability by segment
    plt.subplot(2, 3, 2)
    sns.boxplot(x='segment_name', y='default_probability', data=df)
    plt.title('Default Probability by Segment')
    plt.xticks(rotation=45)
    
    # Credit score by segment
    plt.subplot(2, 3, 3)
    sns.boxplot(x='segment_name', y='credit_score', data=df)
    plt.title('Credit Score by Segment')
    plt.xticks(rotation=45)
    
    # Annual income by segment
    plt.subplot(2, 3, 4)
    sns.boxplot(x='segment_name', y='annual_income', data=df)
    plt.title('Annual Income by Segment')
    plt.xticks(rotation=45)
    
    # Debt-to-income by segment
    plt.subplot(2, 3, 5)
    sns.boxplot(x='segment_name', y='debt_to_income', data=df)
    plt.title('Debt-to-Income Ratio by Segment')
    plt.xticks(rotation=45)
    
    # Employment length by segment
    plt.subplot(2, 3, 6)
    sns.boxplot(x='segment_name', y='employment_length', data=df)
    plt.title('Employment Length by Segment')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('static/img/risk_segmentation/borrower_segment_analysis.png')
    plt.close()
    
    # Create scatter plot of segments
    plt.figure(figsize=(12, 10))
    
    # Credit score vs. debt-to-income
    plt.subplot(2, 2, 1)
    sns.scatterplot(x='credit_score', y='debt_to_income', hue='segment_name', data=df, alpha=0.6)
    plt.title('Credit Score vs. Debt-to-Income by Segment')
    
    # Annual income vs. loan amount
    plt.subplot(2, 2, 2)
    sns.scatterplot(x='annual_income', y='loan_amount', hue='segment_name', data=df, alpha=0.6)
    plt.title('Annual Income vs. Loan Amount by Segment')
    
    # Employment length vs. default probability
    plt.subplot(2, 2, 3)
    sns.scatterplot(x='employment_length', y='default_probability', hue='segment_name', data=df, alpha=0.6)
    plt.title('Employment Length vs. Default Probability by Segment')
    
    # Credit score vs. default probability
    plt.subplot(2, 2, 4)
    sns.scatterplot(x='credit_score', y='default_probability', hue='segment_name', data=df, alpha=0.6)
    plt.title('Credit Score vs. Default Probability by Segment')
    
    plt.tight_layout()
    plt.savefig('static/img/risk_segmentation/borrower_segment_scatter.png')
    plt.close()
    
    return df

# Function to create custom scoring models for different segments
def create_custom_scoring_models(df):
    # Define segment-specific scoring models
    scoring_models = {}
    
    # Get unique segment names
    segments = df['segment_name'].unique()
    
    for segment in segments:
        # Filter data for this segment
        segment_data = df[df['segment_name'] == segment]
        
        # Calculate feature importance for this segment
        # In a real implementation, this would be based on a trained model
        # For this example, we'll use correlation with default probability
        
        features = ['credit_score', 'annual_income', 'debt_to_income', 
                   'loan_amount', 'interest_rate', 'employment_length', 
                   'num_credit_lines', 'num_delinquencies']
        
        correlations = segment_data[features].corrwith(segment_data['default_probability'])
        
        # Convert correlations to importance (absolute value, normalized)
        importance = correlations.abs()
        importance = importance / importance.sum()
        
        # Create scoring model
        scoring_models[segment] = {
            'feature_importance': importance.to_dict(),
            'avg_default_probability': segment_data['default_probability'].mean(),
            'avg_risk_score': segment_data['risk_score'].mean(),
            'sample_size': len(segment_data)
        }
    
    # Save scoring models to JSON
    with open('data/risk_segmentation/custom_scoring_models.json', 'w') as f:
        json.dump(scoring_models, f, indent=4)
    
    # Create visualization of feature importance by segment
    plt.figure(figsize=(15, 10))
    
    # Prepare data for visualization
    importance_data = []
    for segment, model in scoring_models.items():
        for feature, importance in model['feature_importance'].items():
            importance_data.append({
                'Segment': segment,
                'Feature': feature,
                'Importance': importance
            })
    
    importance_df = pd.DataFrame(importance_data)
    
    # Create heatmap
    pivot_df = importance_df.pivot(index='Feature', columns='Segment', values='Importance')
    
    sns.heatmap(pivot_df, annot=True, cmap='YlGnBu', fmt='.3f')
    plt.title('Feature Importance by Borrower Segment')
    plt.tight_layout()
    plt.savefig('static/img/risk_segmentation/feature_importance_by_segment.png')
    plt.close()
    
    # Create bar charts of feature importance for each segment
    for segment in segments:
        plt.figure(figsize=(10, 6))
        
        segment_importance = importance_df[importance_df['Segment'] == segment]
        segment_importance = segment_importance.sort_values('Importance', ascending=False)
        
        sns.barplot(x='Feature', y='Importance', data=segment_importance)
        plt.title(f'Feature Importance for {segment}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'static/img/risk_segmentation/feature_importance_{segment.replace(" ", "_").lower()}.png')
        plt.close()

# Execute all functions to generate the visualizations and data
if __name__ == "__main__":
    print("Generating risk segmentation visualizations and data...")
    df = generate_sample_borrower_data()
    df = create_risk_tiers(df)
    df = create_borrower_segments(df)
    create_custom_scoring_models(df)
    print("Risk segmentation implementation complete!")
