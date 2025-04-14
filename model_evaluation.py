#!/usr/bin/env python3
# Model Evaluation and Optimization for Lending Club Loan Prediction Project

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import time
from sklearn.metrics import roc_auc_score, roc_curve, confusion_matrix, classification_report, precision_recall_curve, average_precision_score
from sklearn.model_selection import learning_curve, validation_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance

# Load trained models
print("Loading trained models...")
with open('trained_models.pkl', 'rb') as f:
    models = pickle.load(f)

# Load preprocessed data
print("Loading preprocessed data...")
with open('preprocessed_data.pkl', 'rb') as f:
    data = pickle.load(f)

X_train = data['X_train']
X_test = data['X_test']
y_train = data['y_train']
y_test = data['y_test']
target_encoder = data['target_encoder']

# Extract the best model (Random Forest)
best_model = models['random_forest']
feature_selector = models['feature_selector']
selected_feature_names = models['selected_feature_names']

print(f"Best model: Random Forest")
print(f"Number of selected features: {len(selected_feature_names)}")

# Apply feature selection to get the selected features
X_train_selected = feature_selector.transform(X_train)
X_test_selected = feature_selector.transform(X_test)

# 1. Detailed Performance Evaluation
print("\n=== Detailed Performance Evaluation ===")

# Get predictions
y_pred = best_model.predict(X_test_selected)
y_pred_proba = best_model.predict_proba(X_test_selected)[:, 1]

# ROC Curve and AUROC
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
auroc = roc_auc_score(y_test, y_pred_proba)

plt.figure(figsize=(10, 8))
plt.plot(fpr, tpr, label=f'Random Forest (AUROC = {auroc:.4f})')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - Random Forest (Detailed)')
plt.legend(loc='lower right')
plt.savefig('random_forest_detailed_roc.png')

# Precision-Recall Curve
precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
avg_precision = average_precision_score(y_test, y_pred_proba)

plt.figure(figsize=(10, 8))
plt.plot(recall, precision, label=f'Random Forest (AP = {avg_precision:.4f})')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve - Random Forest')
plt.legend(loc='upper right')
plt.savefig('random_forest_precision_recall.png')

# Confusion Matrix as a heatmap
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix - Random Forest')
plt.savefig('random_forest_confusion_matrix.png')

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=target_encoder.classes_))

# 2. Feature Importance Analysis
print("\n=== Feature Importance Analysis ===")

# Get feature importances from Random Forest
feature_importances = best_model.feature_importances_
sorted_idx = np.argsort(feature_importances)[::-1]

# Plot feature importances
plt.figure(figsize=(12, 8))
plt.bar(range(len(sorted_idx[:20])), feature_importances[sorted_idx[:20]])
plt.xticks(range(len(sorted_idx[:20])), [selected_feature_names[i] for i in sorted_idx[:20]], rotation=90)
plt.xlabel('Features')
plt.ylabel('Importance')
plt.title('Top 20 Feature Importances - Random Forest')
plt.tight_layout()
plt.savefig('random_forest_feature_importance.png')

# Permutation Importance (more reliable than built-in feature importance)
print("\nCalculating permutation importance...")
perm_importance = permutation_importance(best_model, X_test_selected, y_test, n_repeats=10, random_state=42)
sorted_idx = perm_importance.importances_mean.argsort()[::-1]

# Plot permutation importances
plt.figure(figsize=(12, 8))
plt.bar(range(len(sorted_idx[:20])), perm_importance.importances_mean[sorted_idx[:20]])
plt.xticks(range(len(sorted_idx[:20])), [selected_feature_names[i] for i in sorted_idx[:20]], rotation=90)
plt.xlabel('Features')
plt.ylabel('Permutation Importance')
plt.title('Top 20 Permutation Feature Importances - Random Forest')
plt.tight_layout()
plt.savefig('random_forest_permutation_importance.png')

# 3. Learning Curves
print("\n=== Learning Curves Analysis ===")

# Generate learning curves
train_sizes, train_scores, test_scores = learning_curve(
    best_model, X_train_selected, y_train, 
    train_sizes=np.linspace(0.1, 1.0, 10),
    cv=3, scoring='roc_auc'
)

# Calculate mean and standard deviation
train_mean = np.mean(train_scores, axis=1)
train_std = np.std(train_scores, axis=1)
test_mean = np.mean(test_scores, axis=1)
test_std = np.std(test_scores, axis=1)

# Plot learning curves
plt.figure(figsize=(10, 6))
plt.plot(train_sizes, train_mean, 'o-', color='r', label='Training score')
plt.plot(train_sizes, test_mean, 'o-', color='g', label='Cross-validation score')
plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color='r')
plt.fill_between(train_sizes, test_mean - test_std, test_mean + test_std, alpha=0.1, color='g')
plt.xlabel('Training Examples')
plt.ylabel('Score (AUROC)')
plt.title('Learning Curves - Random Forest')
plt.legend(loc='best')
plt.grid(True)
plt.savefig('random_forest_learning_curves.png')

# 4. Threshold Optimization
print("\n=== Threshold Optimization ===")

# Calculate various metrics at different thresholds
thresholds = np.linspace(0, 1, 100)
metrics = []

for threshold in thresholds:
    y_pred_threshold = (y_pred_proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred_threshold).ravel()
    
    # Calculate metrics
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    metrics.append({
        'threshold': threshold,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    })

# Convert to DataFrame
metrics_df = pd.DataFrame(metrics)

# Plot metrics vs threshold
plt.figure(figsize=(12, 8))
plt.plot(metrics_df['threshold'], metrics_df['accuracy'], label='Accuracy')
plt.plot(metrics_df['threshold'], metrics_df['precision'], label='Precision')
plt.plot(metrics_df['threshold'], metrics_df['recall'], label='Recall')
plt.plot(metrics_df['threshold'], metrics_df['f1'], label='F1 Score')
plt.xlabel('Threshold')
plt.ylabel('Score')
plt.title('Metrics vs Threshold - Random Forest')
plt.legend(loc='best')
plt.grid(True)
plt.savefig('random_forest_threshold_optimization.png')

# Find optimal threshold for F1 score
optimal_idx = metrics_df['f1'].idxmax()
optimal_threshold = metrics_df.loc[optimal_idx, 'threshold']
optimal_f1 = metrics_df.loc[optimal_idx, 'f1']

print(f"Optimal threshold for F1 score: {optimal_threshold:.4f}")
print(f"F1 score at optimal threshold: {optimal_f1:.4f}")

# 5. Model Optimization
print("\n=== Model Optimization ===")

# Create a new Random Forest with optimized parameters
optimized_rf = RandomForestClassifier(
    n_estimators=200,  # Increase number of trees
    max_depth=None,    # Keep unlimited depth
    min_samples_split=2,
    min_samples_leaf=1,
    bootstrap=True,
    class_weight='balanced',  # Use balanced class weights
    random_state=42
)

# Train the optimized model
print("Training optimized Random Forest model...")
start_time = time.time()
optimized_rf.fit(X_train_selected, y_train)
print(f"Training time: {time.time() - start_time:.2f} seconds")

# Evaluate the optimized model
y_pred_opt = optimized_rf.predict(X_test_selected)
y_pred_proba_opt = optimized_rf.predict_proba(X_test_selected)[:, 1]
auroc_opt = roc_auc_score(y_test, y_pred_proba_opt)

print(f"Optimized Random Forest AUROC: {auroc_opt:.4f}")
print("\nOptimized Classification Report:")
print(classification_report(y_test, y_pred_opt, target_names=target_encoder.classes_))

# Compare original vs optimized ROC curves
plt.figure(figsize=(10, 8))
plt.plot(fpr, tpr, label=f'Original Random Forest (AUROC = {auroc:.4f})')

# Calculate ROC curve for optimized model
fpr_opt, tpr_opt, _ = roc_curve(y_test, y_pred_proba_opt)
plt.plot(fpr_opt, tpr_opt, label=f'Optimized Random Forest (AUROC = {auroc_opt:.4f})')

plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve Comparison - Original vs Optimized Random Forest')
plt.legend(loc='lower right')
plt.savefig('random_forest_optimization_comparison.png')

# Save the optimized model
print("\n=== Saving optimized model ===")
models['optimized_random_forest'] = optimized_rf
models['optimal_threshold'] = optimal_threshold

with open('optimized_models.pkl', 'wb') as f:
    pickle.dump(models, f)

print("Optimized models saved to 'optimized_models.pkl'")

# Save a summary of the evaluation and optimization
with open('model_evaluation_summary.txt', 'w') as f:
    f.write("Model Evaluation and Optimization Summary for Lending Club Loan Prediction Project\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("1. Detailed Performance Evaluation\n")
    f.write("-" * 50 + "\n")
    f.write(f"AUROC: {auroc:.4f}\n")
    f.write(f"Average Precision: {avg_precision:.4f}\n")
    f.write("\nConfusion Matrix:\n")
    f.write(str(cm) + "\n\n")
    f.write("Classification Report:\n")
    f.write(classification_report(y_test, y_pred, target_names=target_encoder.classes_) + "\n")
    
    f.write("\n2. Feature Importance Analysis\n")
    f.write("-" * 50 + "\n")
    f.write("Top 10 Important Features (Random Forest):\n")
    for i in range(10):
        idx = sorted_idx[i]
        f.write(f"{selected_feature_names[idx]}: {feature_importances[idx]:.4f}\n")
    
    f.write("\nTop 10 Features (Permutation Importance):\n")
    for i in range(10):
        idx = sorted_idx[i]
        f.write(f"{selected_feature_names[idx]}: {perm_importance.importances_mean[idx]:.4f}\n")
    
    f.write("\n3. Threshold Optimization\n")
    f.write("-" * 50 + "\n")
    f.write(f"Optimal threshold for F1 score: {optimal_threshold:.4f}\n")
    f.write(f"F1 score at optimal threshold: {optimal_f1:.4f}\n")
    
    f.write("\n4. Model Optimization\n")
    f.write("-" * 50 + "\n")
    f.write("Optimized Random Forest Parameters:\n")
    f.write("- n_estimators: 200\n")
    f.write("- max_depth: None\n")
    f.write("- min_samples_split: 2\n")
    f.write("- min_samples_leaf: 1\n")
    f.write("- bootstrap: True\n")
    f.write("- class_weight: balanced\n\n")
    
    f.write(f"Optimized Random Forest AUROC: {auroc_opt:.4f}\n")
    f.write("\nOptimized Classification Report:\n")
    f.write(classification_report(y_test, y_pred_opt, target_names=target_encoder.classes_))

print("Model evaluation summary saved to 'model_evaluation_summary.txt'")
