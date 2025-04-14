import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import GridSearchCV
import joblib
import json
import datetime

# Create directories for enhanced project structure
os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)
os.makedirs('api', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/img', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('utils', exist_ok=True)
os.makedirs('config', exist_ok=True)

# Copy existing model and data files to new structure
os.system('cp preprocessed_data.csv data/ 2>/dev/null || :')
os.system('cp random_forest_model.pkl models/ 2>/dev/null || :')
os.system('cp *.png static/img/ 2>/dev/null || :')

print("Created enhanced project structure")

# Create configuration file
config = {
    "app": {
        "name": "Advanced Loan Prediction System",
        "version": "2.0.0",
        "description": "A sophisticated financial analysis platform with advanced machine learning capabilities"
    },
    "database": {
        "type": "sqlite",  # For development, will be upgraded to PostgreSQL
        "path": "data/loan_prediction.db"
    },
    "api": {
        "version": "v1",
        "base_url": "/api/v1",
        "rate_limit": 100,  # requests per minute
        "enable_documentation": True
    },
    "models": {
        "ensemble": {
            "enabled": True,
            "models": ["random_forest", "gradient_boosting", "neural_network"],
            "voting": "soft"
        },
        "time_series": {
            "enabled": False,  # Will be enabled in future phases
            "lookback_periods": 12
        },
        "macroeconomic": {
            "enabled": False,  # Will be enabled in future phases
            "indicators": ["interest_rate", "unemployment", "inflation", "gdp_growth"]
        }
    },
    "features": {
        "user_accounts": {
            "enabled": False,  # Will be enabled in future phases
            "require_email_verification": True
        },
        "dashboard": {
            "enabled": False,  # Will be enabled in future phases
            "refresh_rate": 3600  # seconds
        },
        "comparison": {
            "enabled": False,  # Will be enabled in future phases
            "max_scenarios": 5
        },
        "batch_processing": {
            "enabled": False,  # Will be enabled in future phases
            "max_batch_size": 1000
        }
    }
}

with open('config/config.json', 'w') as f:
    json.dump(config, f, indent=4)

print("Created configuration file")

# Create database schema
import sqlite3

conn = sqlite3.connect('data/loan_prediction.db')
cursor = conn.cursor()

# Users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
)
''')

# Loan applications table
cursor.execute('''
CREATE TABLE IF NOT EXISTS loan_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    loan_amount REAL NOT NULL,
    interest_rate REAL NOT NULL,
    term INTEGER NOT NULL,
    grade TEXT NOT NULL,
    emp_length INTEGER NOT NULL,
    annual_income REAL NOT NULL,
    debt_to_income REAL NOT NULL,
    verified_income TEXT NOT NULL,
    homeownership TEXT NOT NULL,
    total_credit_lines INTEGER NOT NULL,
    open_credit_lines INTEGER NOT NULL,
    num_mort_accounts INTEGER NOT NULL,
    paid_principal REAL NOT NULL,
    paid_total REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Predictions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    model_name TEXT NOT NULL,
    prediction TEXT NOT NULL,
    probability REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES loan_applications (id)
)
''')

# Economic indicators table
cursor.execute('''
CREATE TABLE IF NOT EXISTS economic_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_name TEXT NOT NULL,
    value REAL NOT NULL,
    region TEXT,
    date DATE NOT NULL,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# API keys table
cursor.execute('''
CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    api_key TEXT UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Webhooks table
cursor.execute('''
CREATE TABLE IF NOT EXISTS webhooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    event_type TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

conn.commit()
conn.close()

print("Created database schema")

# Create API structure
with open('api/__init__.py', 'w') as f:
    f.write('# API package initialization\n')

with open('api/routes.py', 'w') as f:
    f.write('''from flask import Blueprint, request, jsonify
import joblib
import numpy as np
import pandas as pd
import json
import os
import sqlite3
from datetime import datetime

api = Blueprint('api', __name__, url_prefix='/api/v1')

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

# Load models
model_paths = {
    'random_forest': 'models/random_forest_model.pkl',
    'gradient_boosting': 'models/gradient_boosting_model.pkl',
    'neural_network': 'models/neural_network_model.pkl'
}

models = {}
for name, path in model_paths.items():
    if os.path.exists(path):
        models[name] = joblib.load(path)

@api.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Validate required fields
        required_fields = [
            'loan_amount', 'interest_rate', 'term', 'grade', 'emp_length',
            'annual_income', 'debt_to_income', 'verified_income', 'homeownership',
            'total_credit_lines', 'open_credit_lines', 'num_mort_accounts',
            'paid_principal', 'paid_total'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Prepare data for prediction
        input_data = pd.DataFrame([data])
        
        # Make predictions with available models
        results = {}
        for name, model in models.items():
            try:
                probability = model.predict_proba(input_data)[0][1]
                prediction = 'Stand-standing' if probability >= 0.5 else 'Default'
                results[name] = {
                    'prediction': prediction,
                    'probability': float(probability)
                }
            except Exception as e:
                results[name] = {
                    'error': str(e)
                }
        
        # Calculate ensemble result if multiple models available
        if len(results) > 1 and config['models']['ensemble']['enabled']:
            probabilities = [results[name]['probability'] for name in results if 'probability' in results[name]]
            if probabilities:
                ensemble_probability = sum(probabilities) / len(probabilities)
                ensemble_prediction = 'Stand-standing' if ensemble_probability >= 0.5 else 'Default'
                results['ensemble'] = {
                    'prediction': ensemble_prediction,
                    'probability': ensemble_probability
                }
        
        # Store prediction in database if application_id provided
        if 'application_id' in data and results:
            conn = sqlite3.connect('data/loan_prediction.db')
            cursor = conn.cursor()
            
            for model_name, result in results.items():
                if 'probability' in result:
                    cursor.execute(
                        '''INSERT INTO predictions 
                           (application_id, model_name, prediction, probability, created_at) 
                           VALUES (?, ?, ?, ?, ?)''',
                        (data['application_id'], model_name, result['prediction'], 
                         result['probability'], datetime.now())
                    )
            
            conn.commit()
            conn.close()
        
        return jsonify({
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/applications', methods=['GET'])
def get_applications():
    try:
        # Simple API key authentication
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        conn = sqlite3.connect('data/loan_prediction.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verify API key
        cursor.execute('SELECT user_id FROM api_keys WHERE api_key = ? AND is_active = 1', (api_key,))
        key_data = cursor.fetchone()
        
        if not key_data:
            return jsonify({'error': 'Invalid API key'}), 401
        
        user_id = key_data['user_id']
        
        # Update last used timestamp
        cursor.execute('UPDATE api_keys SET last_used = ? WHERE api_key = ?', 
                      (datetime.now(), api_key))
        
        # Get applications for user
        cursor.execute('''
            SELECT * FROM loan_applications 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        
        applications = [dict(row) for row in cursor.fetchall()]
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'applications': applications,
            'count': len(applications)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': config['app']['version'],
        'timestamp': datetime.now().isoformat()
    })
''')

print("Created API structure")

# Create utility functions
with open('utils/__init__.py', 'w') as f:
    f.write('# Utils package initialization\n')

with open('utils/model_utils.py', 'w') as f:
    f.write('''import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import os
import json

def create_ensemble_model(X_train, y_train):
    """
    Create an ensemble model combining Random Forest, Gradient Boosting, and Neural Network
    """
    # Load configuration
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    
    if not config['models']['ensemble']['enabled']:
        # If ensemble is disabled, just return a Random Forest model
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        return {'random_forest': rf}
    
    # Create base models
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
    nn = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
    
    # Train base models
    rf.fit(X_train, y_train)
    gb.fit(X_train, y_train)
    nn.fit(X_train, y_train)
    
    # Create voting ensemble
    voting_type = config['models']['ensemble']['voting']
    ensemble = VotingClassifier(
        estimators=[
            ('rf', rf),
            ('gb', gb),
            ('nn', nn)
        ],
        voting=voting_type
    )
    
    ensemble.fit(X_train, y_train)
    
    # Return all models
    return {
        'random_forest': rf,
        'gradient_boosting': gb,
        'neural_network': nn,
        'ensemble': ensemble
    }

def evaluate_models(models, X_test, y_test):
    """
    Evaluate multiple models and return performance metrics
    """
    results = {}
    
    for name, model in models.items():
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        results[name] = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_prob)
        }
    
    return results

def save_models(models, directory='models'):
    """
    Save models to disk
    """
    os.makedirs(directory, exist_ok=True)
    
    for name, model in models.items():
        joblib.dump(model, f'{directory}/{name}_model.pkl')
    
    return [f'{name}_model.pkl' for name in models.keys()]

def load_models(model_names, directory='models'):
    """
    Load models from disk
    """
    models = {}
    
    for name in model_names:
        path = f'{directory}/{name}_model.pkl'
        if os.path.exists(path):
            models[name] = joblib.load(path)
    
    return models

def feature_importance(model, feature_names):
    """
    Extract feature importance from model
    """
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importances = np.abs(model.coef_[0])
    else:
        return None
    
    return pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)
''')

with open('utils/data_utils.py', 'w') as f:
    f.write('''import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import sqlite3
from datetime import datetime
import requests
import json
import os

def load_economic_indicators():
    """
    Load economic indicators from database or fetch from API if not available
    """
    conn = sqlite3.connect('data/loan_prediction.db')
    cursor = conn.cursor()
    
    # Check if we have recent data
    cursor.execute('''
        SELECT * FROM economic_indicators 
        WHERE date >= date('now', '-30 day')
        ORDER BY date DESC
    ''')
    
    indicators = cursor.fetchall()
    
    if not indicators:
        # Fetch from API (placeholder - would use actual API in production)
        # This is a simulation for development purposes
        sample_indicators = [
            {'indicator_name': 'interest_rate', 'value': 4.5, 'region': 'US', 'date': '2025-04-01', 'source': 'Federal Reserve'},
            {'indicator_name': 'unemployment', 'value': 3.8, 'region': 'US', 'date': '2025-04-01', 'source': 'Bureau of Labor Statistics'},
            {'indicator_name': 'inflation', 'value': 2.3, 'region': 'US', 'date': '2025-04-01', 'source': 'Bureau of Labor Sta
(Content truncated due to size limit. Use line ranges to read in chunks)