from flask import Flask, jsonify, request, render_template
import os
import json

app = Flask(__name__)

# Load configuration
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except:
    config = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/documentation')
def documentation():
    return render_template('documentation.html')

@app.route('/geographic-analysis')
def geographic_analysis():
    return render_template('geographic_analysis.html')

@app.route('/financial-planning')
def financial_planning():
    return render_template('financial_planning.html')

@app.route('/risk-segmentation')
def risk_segmentation():
    return render_template('risk_segmentation.html')

@app.route('/competitive-analysis')
def competitive_analysis():
    return render_template('competitive_analysis.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Calculate risk factors
        risk_factors = []
        
        # Income factor (higher income = lower risk)
        income = float(data.get('annual_income', 0))
        income_factor = min(income / 100000, 1.0) * 0.25
        risk_factors.append(income_factor)
        
        # Debt-to-income factor (lower ratio = lower risk)
        dti = float(data.get('debt_to_income', 0))
        dti_factor = (1 - min(dti / 50, 1.0)) * 0.2
        risk_factors.append(dti_factor)
        
        # Grade factor
        grade_mapping = {'A': 0.2, 'B': 0.15, 'C': 0.1, 'D': 0.05, 'E': 0.0, 'F': -0.05, 'G': -0.1}
        grade_factor = grade_mapping.get(data.get('grade', 'C'), 0)
        risk_factors.append(grade_factor)
        
        # Employment length factor
        emp_length = float(data.get('emp_length', 0))
        emp_factor = min(emp_length / 10, 1.0) * 0.15
        risk_factors.append(emp_factor)
        
        # Calculate final probability
        probability = sum(risk_factors) + 0.5
        prediction = 'Good Standing' if probability >= 0.5 else 'Default Risk'
        
        return jsonify({
            'prediction': prediction,
            'probability': round(probability, 2),
            'risk_factors': {
                'income_contribution': round(income_factor, 2),
                'dti_contribution': round(dti_factor, 2),
                'grade_contribution': round(grade_factor, 2),
                'employment_contribution': round(emp_factor, 2)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "config_loaded": bool(config)
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error=str(e)), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True) 