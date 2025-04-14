import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load and preprocess the data
print("Loading data...")
df = pd.read_csv('loan_data.csv')

# Define features for the model
features = [
    'credit_score', 'annual_income', 'loan_amount', 'term', 'interest_rate',
    'employment_length', 'debt_to_income', 'total_credit_lines', 'open_credit_lines',
    'num_mortgage_accounts', 'paid_principal', 'paid_total'
]

# Convert categorical variables to numeric
categorical_features = {
    'grade': {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7},
    'verified_income': {'Not Verified': 0, 'Source Verified': 1, 'Verified': 2},
    'homeownership': {'RENT': 0, 'OWN': 1, 'MORTGAGE': 2, 'OTHER': 3}
}

for feature, mapping in categorical_features.items():
    df[feature] = df[feature].map(mapping)
    features.append(feature)

# Prepare features and target
X = df[features]
y = df['loan_status']  # Assuming 'loan_status' is your target variable

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
print("Scaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the model
print("Training model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate the model
train_score = model.score(X_train_scaled, y_train)
test_score = model.score(X_test_scaled, y_test)
print(f"Training accuracy: {train_score:.4f}")
print(f"Testing accuracy: {test_score:.4f}")

# Save the model and scaler
print("Saving model and scaler...")
joblib.dump(model, 'loan_prediction_model.joblib')
joblib.dump(scaler, 'scaler.joblib')

print("Training complete! Model and scaler have been saved.") 