#!/usr/bin/env python3
# Model Development with Reduced Complexity for Lending Club Loan Prediction Project

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import time
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, roc_curve, confusion_matrix, classification_report
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.feature_selection import SelectFromModel, SelectKBest, f_classif

# Load preprocessed data
print("Loading preprocessed data...")
with open('preprocessed_data.pkl', 'rb') as f:
    data = pickle.load(f)

X_train = data['X_train']
X_test = data['X_test']
y_train = data['y_train']
y_test = data['y_test']
feature_names = data['feature_names']
target_encoder = data['target_encoder']

print(f"Training set shape: {X_train.shape}")
print(f"Testing set shape: {X_test.shape}")
print(f"Target encoding: {dict(zip(target_encoder.classes_, target_encoder.transform(target_encoder.classes_)))}")

# Step 1: Feature Selection to reduce dimensionality
print("\n=== Performing Feature Selection ===")
print(f"Original number of features: {X_train.shape[1]}")

# Method 1: Select top K features using ANOVA F-value
k_best = 100  # Select top 100 features
selector = SelectKBest(f_classif, k=k_best)
X_train_selected = selector.fit_transform(X_train, y_train)
X_test_selected = selector.transform(X_test)

# Get selected feature indices
selected_indices = selector.get_support(indices=True)
selected_feature_names = [feature_names[i] for i in selected_indices]

print(f"Number of features after SelectKBest: {X_train_selected.shape[1]}")
print(f"Top 10 selected features: {selected_feature_names[:10]}")

# Function to evaluate model performance
def evaluate_model(model, X_test, y_test, model_name):
    # Predict probabilities
    if hasattr(model, 'predict_proba'):
        y_pred_proba = model.predict_proba(X_test)[:, 1]
    else:
        # For models that don't have predict_proba (like LinearSVC)
        decision_scores = model.decision_function(X_test)
        # Scale to [0, 1] for ROC curve
        y_pred_proba = (decision_scores - decision_scores.min()) / (decision_scores.max() - decision_scores.min())
    
    # Calculate AUROC
    auroc = roc_auc_score(y_test, y_pred_proba)
    
    # Get predictions
    y_pred = model.predict(X_test)
    
    # Print evaluation metrics
    print(f"\n=== {model_name} Evaluation ===")
    print(f"AUROC: {auroc:.4f}")
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=target_encoder.classes_))
    
    # Plot ROC curve
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'{model_name} (AUROC = {auroc:.4f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curve - {model_name}')
    plt.legend(loc='lower right')
    plt.savefig(f'{model_name.replace(" ", "_").lower()}_roc_curve.png')
    
    return {
        'model_name': model_name,
        'auroc': auroc,
        'confusion_matrix': cm,
        'y_pred': y_pred,
        'y_pred_proba': y_pred_proba
    }

# 1. Logistic Regression (memory-efficient alternative to SVM)
print("\n=== Training Logistic Regression ===")
start_time = time.time()

# Define parameter grid for Logistic Regression
param_grid_lr = {
    'C': [0.01, 0.1, 1.0],
    'solver': ['liblinear'],
    'max_iter': [100]
}

# Initialize Logistic Regression
lr = LogisticRegression(random_state=42)

# Perform grid search with cross-validation
print("Performing grid search for Logistic Regression...")
grid_search_lr = GridSearchCV(
    estimator=lr,
    param_grid=param_grid_lr,
    cv=3,
    scoring='roc_auc',
    n_jobs=-1
)

# Fit the grid search to the data
grid_search_lr.fit(X_train_selected, y_train)

# Get the best model
best_lr = grid_search_lr.best_estimator_
print(f"Best Logistic Regression parameters: {grid_search_lr.best_params_}")
print(f"Best Logistic Regression cross-validation score: {grid_search_lr.best_score_:.4f}")
print(f"Logistic Regression training time: {time.time() - start_time:.2f} seconds")

# Evaluate Logistic Regression
lr_results = evaluate_model(best_lr, X_test_selected, y_test, "Logistic Regression")

# 2. Naive Bayes (memory-efficient)
print("\n=== Training Naive Bayes ===")
start_time = time.time()

# Initialize Naive Bayes
nb = GaussianNB()

# Train the model
nb.fit(X_train_selected, y_train)
print(f"Naive Bayes training time: {time.time() - start_time:.2f} seconds")

# Evaluate Naive Bayes
nb_results = evaluate_model(nb, X_test_selected, y_test, "Naive Bayes")

# 3. Random Forest (as an alternative to Neural Network)
print("\n=== Training Random Forest ===")
start_time = time.time()

# Define parameter grid for Random Forest
param_grid_rf = {
    'n_estimators': [50, 100],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5]
}

# Initialize Random Forest
rf = RandomForestClassifier(random_state=42)

# Perform randomized search with cross-validation to save memory
print("Performing randomized search for Random Forest...")
random_search_rf = RandomizedSearchCV(
    estimator=rf,
    param_distributions=param_grid_rf,
    n_iter=5,  # Try only 5 combinations
    cv=3,
    scoring='roc_auc',
    n_jobs=-1,
    random_state=42
)

# Fit the randomized search to the data
random_search_rf.fit(X_train_selected, y_train)

# Get the best model
best_rf = random_search_rf.best_estimator_
print(f"Best Random Forest parameters: {random_search_rf.best_params_}")
print(f"Best Random Forest cross-validation score: {random_search_rf.best_score_:.4f}")
print(f"Random Forest training time: {time.time() - start_time:.2f} seconds")

# Evaluate Random Forest
rf_results = evaluate_model(best_rf, X_test_selected, y_test, "Random Forest")

# 4. Neural Network with simplified architecture
print("\n=== Training Neural Network (Simplified) ===")
start_time = time.time()

# Initialize Neural Network with a simple architecture
nn = MLPClassifier(
    hidden_layer_sizes=(50,),  # Single hidden layer with 50 neurons
    activation='relu',
    solver='adam',
    max_iter=200,
    random_state=42
)

# Train the model
nn.fit(X_train_selected, y_train)
print(f"Neural Network training time: {time.time() - start_time:.2f} seconds")

# Evaluate Neural Network
nn_results = evaluate_model(nn, X_test_selected, y_test, "Neural Network")

# Compare models
print("\n=== Model Comparison ===")
models = [lr_results, nb_results, rf_results, nn_results]
model_names = [model['model_name'] for model in models]
auroc_scores = [model['auroc'] for model in models]

# Plot comparison
plt.figure(figsize=(10, 6))
plt.bar(model_names, auroc_scores)
plt.xlabel('Model')
plt.ylabel('AUROC Score')
plt.title('Model Comparison - AUROC Scores')
plt.ylim(0, 1)
for i, v in enumerate(auroc_scores):
    plt.text(i, v + 0.02, f"{v:.4f}", ha='center')
plt.savefig('model_comparison.png')

# Plot ROC curves for all models
plt.figure(figsize=(10, 8))
for model in models:
    fpr, tpr, _ = roc_curve(y_test, model['y_pred_proba'])
    plt.plot(fpr, tpr, label=f"{model['model_name']} (AUROC = {model['auroc']:.4f})")

plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves - All Models')
plt.legend(loc='lower right')
plt.savefig('all_models_roc_curve.png')

# Save models
print("\n=== Saving models ===")
models_to_save = {
    'logistic_regression': best_lr,
    'naive_bayes': nb,
    'random_forest': best_rf,
    'neural_network': nn,
    'target_encoder': target_encoder,
    'feature_selector': selector,
    'selected_feature_names': selected_feature_names
}

with open('trained_models.pkl', 'wb') as f:
    pickle.dump(models_to_save, f)

print("Models saved to 'trained_models.pkl'")

# Determine the best model
best_model_idx = np.argmax(auroc_scores)
best_model_name = model_names[best_model_idx]
best_model_auroc = auroc_scores[best_model_idx]

print(f"\nBest performing model: {best_model_name} with AUROC = {best_model_auroc:.4f}")

# Save a summary of model performance
with open('model_performance_summary.txt', 'w') as f:
    f.write("Model Performance Summary for Lending Club Loan Prediction Project\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("Feature Selection:\n")
    f.write(f"Original number of features: {X_train.shape[1]}\n")
    f.write(f"Number of features after selection: {X_train_selected.shape[1]}\n")
    f.write(f"Top 10 selected features: {selected_feature_names[:10]}\n\n")
    
    f.write("Model Comparison - AUROC Scores:\n")
    for model_name, auroc in zip(model_names, auroc_scores):
        f.write(f"{model_name}: {auroc:.4f}\n")
    
    f.write(f"\nBest performing model: {best_model_name} with AUROC = {best_model_auroc:.4f}\n\n")
    
    # Write detailed results for each model
    for model in models:
        f.write(f"\n{model['model_name']} Results:\n")
        f.write("-" * 50 + "\n")
        f.write(f"AUROC: {model['auroc']:.4f}\n")
        f.write("\nConfusion Matrix:\n")
        f.write(str(model['confusion_matrix']) + "\n")
        
        # Calculate and write additional metrics
        tn, fp, fn, tp = model['confusion_matrix'].ravel()
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        f.write(f"\nAccuracy: {accuracy:.4f}\n")
        f.write(f"Precision: {precision:.4f}\n")
        f.write(f"Recall: {recall:.4f}\n")
        f.write(f"F1 Score: {f1:.4f}\n")

print("Model performance summary saved to 'model_performance_summary.txt'")
