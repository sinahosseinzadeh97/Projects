import pandas as pd
import numpy as np
import os
import joblib
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from utils.model_utils import create_ensemble_model, evaluate_models, save_models, feature_importance

print("Starting implementation of ensemble models...")

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

# Update configuration to enable ensemble models
config['models']['ensemble']['enabled'] = True
with open('config/config.json', 'w') as f:
    json.dump(config, f, indent=4)

print("Ensemble models enabled in configuration")

# Load preprocessed data
try:
    data = pd.read_csv('data/preprocessed_data.csv')
    print(f"Loaded preprocessed data with {data.shape[0]} rows and {data.shape[1]} columns")
except FileNotFoundError:
    # If preprocessed data doesn't exist, load and preprocess the original data
    try:
        data = pd.read_csv('data/loans_full_schema.csv')
        print(f"Loaded original data with {data.shape[0]} rows and {data.shape[1]} columns")
        
        # Basic preprocessing
        # Convert loan_status to binary target (1 for 'Fully Paid', 0 for others)
        if 'loan_status' in data.columns:
            data['loan_status_binary'] = data['loan_status'].apply(lambda x: 1 if x == 'Fully Paid' else 0)
        else:
            # Create a synthetic target if loan_status doesn't exist
            print("Creating synthetic target for demonstration")
            data['loan_status_binary'] = np.random.binomial(1, 0.7, data.shape[0])
        
        # Handle missing values
        data = data.fillna(data.median(numeric_only=True))
        
        # Select features (adjust based on available columns)
        numeric_features = [col for col in data.select_dtypes(include=['int64', 'float64']).columns 
                           if col != 'loan_status_binary' and data[col].nunique() > 1]
        categorical_features = [col for col in data.select_dtypes(include=['object']).columns 
                               if col != 'loan_status' and data[col].nunique() > 1 and data[col].nunique() < 20]
        
        # Save preprocessed data
        data.to_csv('data/preprocessed_data.csv', index=False)
        print(f"Saved preprocessed data with {len(numeric_features)} numeric and {len(categorical_features)} categorical features")
    except FileNotFoundError:
        print("Error: No data file found. Please ensure data is available in the data directory.")
        exit(1)

# Prepare data for modeling
# Identify target variable
target_col = 'loan_status_binary' if 'loan_status_binary' in data.columns else None

if target_col is None:
    print("Error: Target variable not found in the dataset.")
    exit(1)

# Select features
X = data.drop([target_col], axis=1)
if 'loan_status' in X.columns:
    X = X.drop(['loan_status'], axis=1)
y = data[target_col]

# Identify numeric and categorical features
numeric_features = list(X.select_dtypes(include=['int64', 'float64']).columns)
categorical_features = list(X.select_dtypes(include=['object']).columns)

print(f"Features: {len(numeric_features)} numeric, {len(categorical_features)} categorical")

# Create preprocessing pipeline
numeric_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training set: {X_train.shape[0]} samples, Test set: {X_test.shape[0]} samples")

# Fit preprocessor
print("Fitting preprocessor...")
X_train_preprocessed = preprocessor.fit_transform(X_train)
X_test_preprocessed = preprocessor.transform(X_test)

# Save preprocessor
joblib.dump(preprocessor, 'models/preprocessor.pkl')
print("Saved preprocessor to models/preprocessor.pkl")

# Create and train individual models
print("Training individual models...")

# Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train_preprocessed, y_train)
rf_pred = rf.predict(X_test_preprocessed)
rf_prob = rf.predict_proba(X_test_preprocessed)[:, 1]
print(f"Random Forest - Accuracy: {accuracy_score(y_test, rf_pred):.4f}, ROC AUC: {roc_auc_score(y_test, rf_prob):.4f}")

# Gradient Boosting
gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
gb.fit(X_train_preprocessed, y_train)
gb_pred = gb.predict(X_test_preprocessed)
gb_prob = gb.predict_proba(X_test_preprocessed)[:, 1]
print(f"Gradient Boosting - Accuracy: {accuracy_score(y_test, gb_pred):.4f}, ROC AUC: {roc_auc_score(y_test, gb_prob):.4f}")

# Neural Network
nn = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
nn.fit(X_train_preprocessed, y_train)
nn_pred = nn.predict(X_test_preprocessed)
nn_prob = nn.predict_proba(X_test_preprocessed)[:, 1]
print(f"Neural Network - Accuracy: {accuracy_score(y_test, nn_pred):.4f}, ROC AUC: {roc_auc_score(y_test, nn_prob):.4f}")

# Create ensemble model
print("Creating ensemble model...")
ensemble = VotingClassifier(
    estimators=[
        ('rf', rf),
        ('gb', gb),
        ('nn', nn)
    ],
    voting='soft'
)
ensemble.fit(X_train_preprocessed, y_train)
ensemble_pred = ensemble.predict(X_test_preprocessed)
ensemble_prob = ensemble.predict_proba(X_test_preprocessed)[:, 1]
print(f"Ensemble - Accuracy: {accuracy_score(y_test, ensemble_pred):.4f}, ROC AUC: {roc_auc_score(y_test, ensemble_prob):.4f}")

# Save all models
models = {
    'random_forest': rf,
    'gradient_boosting': gb,
    'neural_network': nn,
    'ensemble': ensemble
}
for name, model in models.items():
    joblib.dump(model, f'models/{name}_model.pkl')
print("Saved all models to models/ directory")

# Create ROC curve visualization
plt.figure(figsize=(10, 8))
plt.plot([0, 1], [0, 1], 'k--')

# Plot ROC curves for all models
fpr_rf, tpr_rf, _ = roc_curve(y_test, rf_prob)
plt.plot(fpr_rf, tpr_rf, label=f'Random Forest (AUC = {roc_auc_score(y_test, rf_prob):.3f})')

fpr_gb, tpr_gb, _ = roc_curve(y_test, gb_prob)
plt.plot(fpr_gb, tpr_gb, label=f'Gradient Boosting (AUC = {roc_auc_score(y_test, gb_prob):.3f})')

fpr_nn, tpr_nn, _ = roc_curve(y_test, nn_prob)
plt.plot(fpr_nn, tpr_nn, label=f'Neural Network (AUC = {roc_auc_score(y_test, nn_prob):.3f})')

fpr_ensemble, tpr_ensemble, _ = roc_curve(y_test, ensemble_prob)
plt.plot(fpr_ensemble, tpr_ensemble, label=f'Ensemble (AUC = {roc_auc_score(y_test, ensemble_prob):.3f})')

plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves for Loan Default Prediction Models')
plt.legend(loc='best')
plt.savefig('static/img/ensemble_roc_curves.png')
print("Saved ROC curve visualization to static/img/ensemble_roc_curves.png")

# Create feature importance visualization for Random Forest
if hasattr(rf, 'feature_importances_'):
    # Get feature names after one-hot encoding
    feature_names = []
    for name, transformer, features in preprocessor.transformers_:
        if name == 'num':
            feature_names.extend(features)
        elif name == 'cat':
            for feature in features:
                categories = transformer.named_steps['onehot'].categories_[features.index(feature)]
                feature_names.extend([f"{feature}_{category}" for category in categories])
    
    # Limit to top 20 features if there are many
    if len(feature_names) > 20:
        indices = np.argsort(rf.feature_importances_)[-20:]
        plt.figure(figsize=(10, 8))
        plt.barh(range(20), rf.feature_importances_[indices])
        plt.yticks(range(20), [feature_names[i] if i < len(feature_names) else f"Feature {i}" for i in indices])
    else:
        indices = np.argsort(rf.feature_importances_)
        plt.figure(figsize=(10, 8))
        plt.barh(range(len(indices)), rf.feature_importances_[indices])
        plt.yticks(range(len(indices)), [feature_names[i] if i < len(feature_names) else f"Feature {i}" for i in indices])
    
    plt.xlabel('Feature Importance')
    plt.title('Random Forest Feature Importance')
    plt.tight_layout()
    plt.savefig('static/img/ensemble_feature_importance.png')
    print("Saved feature importance visualization to static/img/ensemble_feature_importance.png")

# Create model comparison visualization
models_comparison = {
    'Random Forest': {
        'Accuracy': accuracy_score(y_test, rf_pred),
        'Precision': precision_score(y_test, rf_pred),
        'Recall': recall_score(y_test, rf_pred),
        'F1 Score': f1_score(y_test, rf_pred),
        'ROC AUC': roc_auc_score(y_test, rf_prob)
    },
    'Gradient Boosting': {
        'Accuracy': accuracy_score(y_test, gb_pred),
        'Precision': precision_score(y_test, gb_pred),
        'Recall': recall_score(y_test, gb_pred),
        'F1 Score': f1_score(y_test, gb_pred),
        'ROC AUC': roc_auc_score(y_test, gb_prob)
    },
    'Neural Network': {
        'Accuracy': accuracy_score(y_test, nn_pred),
        'Precision': precision_score(y_test, nn_pred),
        'Recall': recall_score(y_test, nn_pred),
        'F1 Score': f1_score(y_test, nn_pred),
        'ROC AUC': roc_auc_score(y_test, nn_prob)
    },
    'Ensemble': {
        'Accuracy': accuracy_score(y_test, ensemble_pred),
        'Precision': precision_score(y_test, ensemble_pred),
        'Recall': recall_score(y_test, ensemble_pred),
        'F1 Score': f1_score(y_test, ensemble_pred),
        'ROC AUC': roc_auc_score(y_test, ensemble_prob)
    }
}

# Convert to DataFrame for easier plotting
comparison_df = pd.DataFrame(models_comparison).T
comparison_df.plot(kind='bar', figsize=(12, 8))
plt.title('Model Performance Comparison')
plt.ylabel('Score')
plt.xlabel('Model')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('static/img/ensemble_model_comparison.png')
print("Saved model comparison visualization to static/img/ensemble_model_comparison.png")

# Save comparison results to JSON for use in the web application
with open('static/js/model_comparison.json', 'w') as f:
    json.dump(models_comparison, f, indent=4)
print("Saved model comparison data to static/js/model_comparison.json")

print("Ensemble models implementation completed successfully!")
