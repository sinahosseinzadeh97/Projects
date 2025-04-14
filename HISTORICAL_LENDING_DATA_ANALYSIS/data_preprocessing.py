#!/usr/bin/env python3
# Data Preprocessing for Lending Club Loan Prediction Project

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.combine import SMOTEENN
import pickle

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)

print("Loading dataset...")
df = pd.read_csv('loans_full_schema.csv')

# Display basic information
print(f"Original dataset shape: {df.shape}")

# Step 1: Define target variable
# Based on the exploration, we need to convert loan_status into a binary classification problem
# We'll define "Default" as loans that are Late or Charged Off, and "Stand-standing" as Current or Fully Paid
print("\n=== Converting target variable to binary classification ===")
print("Original loan_status distribution:")
print(df['loan_status'].value_counts())

# Create binary target variable
df['loan_status_binary'] = df['loan_status'].apply(
    lambda x: 'Default' if x in ['Late (16-30 days)', 'Late (31-120 days)', 'Charged Off'] else 'Stand-standing'
)

print("\nBinary loan_status distribution:")
print(df['loan_status_binary'].value_counts())
print(df['loan_status_binary'].value_counts(normalize=True) * 100)

# Step 2: Handle missing values
print("\n=== Handling missing values ===")
# Check missing values
missing_values = df.isnull().sum()
missing_percent = (missing_values / len(df)) * 100
missing_df = pd.DataFrame({
    'Missing Values': missing_values,
    'Percentage': missing_percent
})
print(missing_df[missing_df['Missing Values'] > 0].sort_values('Missing Values', ascending=False))

# Drop columns with high percentage of missing values (>50%)
high_missing_cols = missing_df[missing_df['Percentage'] > 50].index.tolist()
print(f"\nDropping columns with >50% missing values: {high_missing_cols}")
df = df.drop(columns=high_missing_cols)

# For numerical columns with missing values, use median imputation
numerical_features = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
numerical_features_with_missing = [col for col in numerical_features if df[col].isnull().sum() > 0]

if numerical_features_with_missing:
    print(f"\nImputing missing values for numerical features: {numerical_features_with_missing}")
    numerical_imputer = SimpleImputer(strategy='median')
    df[numerical_features_with_missing] = numerical_imputer.fit_transform(df[numerical_features_with_missing])

# For categorical columns with missing values, fill with 'Missing'
categorical_features = df.select_dtypes(include=['object']).columns.tolist()
categorical_features_with_missing = [col for col in categorical_features if df[col].isnull().sum() > 0]

if categorical_features_with_missing:
    print(f"\nImputing missing values for categorical features: {categorical_features_with_missing}")
    for col in categorical_features_with_missing:
        df[col] = df[col].fillna('Missing')

# Step 3: Feature selection
print("\n=== Feature selection ===")
# Drop unnecessary columns
# These might include ID columns, redundant features, or features with too many categories
columns_to_drop = ['loan_status']  # We've created loan_status_binary
print(f"Dropping unnecessary columns: {columns_to_drop}")
df = df.drop(columns=columns_to_drop)

# Step 4: Encode categorical variables
print("\n=== Encoding categorical variables ===")
# Identify categorical columns (excluding the target)
categorical_features = [col for col in df.select_dtypes(include=['object']).columns if col != 'loan_status_binary']
print(f"Categorical features to encode: {categorical_features}")

# For binary categorical features, use Label Encoding
binary_features = [col for col in categorical_features if df[col].nunique() == 2]
if binary_features:
    print(f"\nApplying Label Encoding to binary features: {binary_features}")
    label_encoders = {}
    for col in binary_features:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le

# For categorical features with multiple categories, use One-Hot Encoding
multi_features = [col for col in categorical_features if col not in binary_features and col != 'loan_status_binary']
if multi_features:
    print(f"\nApplying One-Hot Encoding to multi-category features: {multi_features}")
    df = pd.get_dummies(df, columns=multi_features, drop_first=True)

# Encode the target variable
print("\nEncoding target variable")
target_encoder = LabelEncoder()
df['loan_status_binary'] = target_encoder.fit_transform(df['loan_status_binary'])
print(f"Target encoding mapping: {dict(zip(target_encoder.classes_, target_encoder.transform(target_encoder.classes_)))}")

# Step 5: Feature scaling
print("\n=== Feature scaling ===")
# Identify numerical features for scaling (excluding the target)
numerical_features = [col for col in df.select_dtypes(include=['int64', 'float64']).columns if col != 'loan_status_binary']
print(f"Scaling {len(numerical_features)} numerical features")

# Apply StandardScaler
scaler = StandardScaler()
df[numerical_features] = scaler.fit_transform(df[numerical_features])

# Step 6: Handle class imbalance
print("\n=== Handling class imbalance ===")
# Split the data into features and target
X = df.drop(columns=['loan_status_binary'])
y = df['loan_status_binary']

print(f"Class distribution before handling imbalance:")
print(pd.Series(y).value_counts())
print(pd.Series(y).value_counts(normalize=True) * 100)

# Apply SMOTE to handle class imbalance
print("\nApplying SMOTE to balance the classes")
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

print(f"Class distribution after SMOTE:")
print(pd.Series(y_resampled).value_counts())
print(pd.Series(y_resampled).value_counts(normalize=True) * 100)

# Step 7: Train-test split
print("\n=== Train-test split ===")
X_train, X_test, y_train, y_test = train_test_split(
    X_resampled, y_resampled, test_size=0.2, random_state=42, stratify=y_resampled
)

print(f"Training set shape: {X_train.shape}")
print(f"Testing set shape: {X_test.shape}")

# Step 8: Save preprocessed data
print("\n=== Saving preprocessed data ===")
# Save the preprocessed data
preprocessed_data = {
    'X_train': X_train,
    'X_test': X_test,
    'y_train': y_train,
    'y_test': y_test,
    'feature_names': X.columns.tolist(),
    'target_encoder': target_encoder,
    'scaler': scaler
}

with open('preprocessed_data.pkl', 'wb') as f:
    pickle.dump(preprocessed_data, f)

print("Preprocessing completed. Preprocessed data saved to 'preprocessed_data.pkl'")

# Save a summary of preprocessing steps
with open('preprocessing_summary.txt', 'w') as f:
    f.write("Preprocessing Summary for Lending Club Loan Prediction Project\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"Original dataset shape: {df.shape}\n")
    f.write(f"Columns dropped due to high missing values: {high_missing_cols}\n")
    f.write(f"Numerical features with imputed missing values: {numerical_features_with_missing}\n")
    f.write(f"Categorical features with imputed missing values: {categorical_features_with_missing}\n")
    f.write(f"Unnecessary columns dropped: {columns_to_drop}\n")
    f.write(f"Binary categorical features encoded: {binary_features}\n")
    f.write(f"Multi-category features one-hot encoded: {multi_features}\n")
    f.write(f"Target encoding mapping: {dict(zip(target_encoder.classes_, target_encoder.transform(target_encoder.classes_)))}\n")
    f.write(f"Number of numerical features scaled: {len(numerical_features)}\n")
    f.write(f"Class distribution before SMOTE: {pd.Series(y).value_counts().to_dict()}\n")
    f.write(f"Class distribution after SMOTE: {pd.Series(y_resampled).value_counts().to_dict()}\n")
    f.write(f"Training set shape: {X_train.shape}\n")
    f.write(f"Testing set shape: {X_test.shape}\n")

print("Preprocessing summary saved to 'preprocessing_summary.txt'")
