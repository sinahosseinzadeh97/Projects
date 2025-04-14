import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

class LoanPredictor:
    def __init__(self):
        # Initialize with default model or load from file if exists
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model_path = os.path.join(os.path.dirname(__file__), 'loan_predictor_model.joblib')
        
        # Try to load existing model
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
    
    def preprocess_data(self, data):
        # Convert input data to numpy array
        features = np.array([
            float(data.get('loan_amount', 0)),
            float(data.get('interest_rate', 0)),
            float(data.get('term', 0)),
            ord(data.get('grade', 'A')) - ord('A'),  # Convert grade to numeric
            float(data.get('emp_length', 0)),
            float(data.get('annual_income', 0)),
            float(data.get('debt_to_income', 0)),
            1 if data.get('verified_income') == 'Verified' else 0,
            1 if data.get('homeownership') == 'OWN' else 0,
            float(data.get('total_credit_lines', 0)),
            float(data.get('open_credit_lines', 0)),
            float(data.get('num_mort_accounts', 0)),
            float(data.get('paid_principal', 0)),
            float(data.get('paid_total', 0))
        ]).reshape(1, -1)
        
        return features
    
    def predict(self, data):
        try:
            # Preprocess the input data
            features = self.preprocess_data(data)
            
            # Make prediction
            prediction = self.model.predict(features)[0]
            
            # Return 1 for good loan, 0 for bad loan
            return int(prediction)
        except Exception as e:
            raise ValueError(f"Error in prediction: {str(e)}")
    
    def train(self, X, y):
        """Train the model with new data"""
        self.model.fit(X, y)
        # Save the trained model
        joblib.dump(self.model, self.model_path) 