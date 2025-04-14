#!/usr/bin/env python3
# Data Exploration for Lending Club Loan Prediction Project

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('loans_full_schema.csv')

# Basic information about the dataset
print("\n=== Dataset Information ===")
print(f"Dataset shape: {df.shape}")
print(f"Number of rows: {df.shape[0]}")
print(f"Number of columns: {df.shape[1]}")

# Display first few rows
print("\n=== First 5 rows of the dataset ===")
print(df.head())

# Column information
print("\n=== Column information ===")
print(df.info())

# Summary statistics
print("\n=== Summary statistics ===")
print(df.describe())

# Check for missing values
print("\n=== Missing values ===")
missing_values = df.isnull().sum()
missing_percent = (missing_values / len(df)) * 100
missing_df = pd.DataFrame({
    'Missing Values': missing_values,
    'Percentage': missing_percent
})
print(missing_df[missing_df['Missing Values'] > 0].sort_values('Missing Values', ascending=False))

# Check the target variable (loan_status)
print("\n=== Target variable (loan_status) distribution ===")
if 'loan_status' in df.columns:
    print(df['loan_status'].value_counts())
    print("\nPercentage distribution:")
    print(df['loan_status'].value_counts(normalize=True) * 100)
    
    # Plot the distribution
    plt.figure(figsize=(10, 6))
    sns.countplot(x='loan_status', data=df)
    plt.title('Distribution of Loan Status')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('loan_status_distribution.png')
else:
    print("'loan_status' column not found in the dataset.")

# Explore key numerical features
print("\n=== Key numerical features ===")
numerical_features = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
if 'loan_amount' in numerical_features:
    plt.figure(figsize=(10, 6))
    sns.histplot(df['loan_amount'], kde=True)
    plt.title('Distribution of Loan Amount')
    plt.tight_layout()
    plt.savefig('loan_amount_distribution.png')

if 'interest_rate' in numerical_features:
    plt.figure(figsize=(10, 6))
    sns.histplot(df['interest_rate'], kde=True)
    plt.title('Distribution of Interest Rate')
    plt.tight_layout()
    plt.savefig('interest_rate_distribution.png')

# Explore key categorical features
print("\n=== Key categorical features ===")
categorical_features = df.select_dtypes(include=['object']).columns.tolist()
for feature in categorical_features[:5]:  # Limit to first 5 categorical features
    print(f"\nDistribution of {feature}:")
    print(df[feature].value_counts().head(10))  # Show top 10 categories

# Relationship between loan status and other features
if 'loan_status' in df.columns:
    print("\n=== Relationship between loan status and key features ===")
    
    # Loan amount vs loan status
    if 'loan_amount' in df.columns:
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='loan_status', y='loan_amount', data=df)
        plt.title('Loan Amount by Loan Status')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('loan_amount_by_status.png')
    
    # Interest rate vs loan status
    if 'interest_rate' in df.columns:
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='loan_status', y='interest_rate', data=df)
        plt.title('Interest Rate by Loan Status')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('interest_rate_by_status.png')
    
    # Grade vs loan status (if available)
    if 'grade' in df.columns:
        plt.figure(figsize=(12, 6))
        cross_tab = pd.crosstab(df['grade'], df['loan_status'], normalize='index') * 100
        cross_tab.plot(kind='bar', stacked=True)
        plt.title('Loan Status by Grade')
        plt.xlabel('Grade')
        plt.ylabel('Percentage')
        plt.tight_layout()
        plt.savefig('loan_status_by_grade.png')

# Correlation matrix for numerical features
print("\n=== Correlation matrix for numerical features ===")
numerical_df = df.select_dtypes(include=['int64', 'float64'])
correlation_matrix = numerical_df.corr()

plt.figure(figsize=(16, 12))
sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Matrix of Numerical Features')
plt.tight_layout()
plt.savefig('correlation_matrix.png')

print("\nData exploration completed. Visualizations saved as PNG files.")
