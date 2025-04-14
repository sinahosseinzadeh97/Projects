import os
import json
import sqlite3
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

print("Starting implementation of loan recommendation engine...")

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

# Update configuration to enable recommendation engine
config['features']['recommendation_engine']['enabled'] = True
with open('config/config.json', 'w') as f:
    json.dump(config, f, indent=4)

print("Recommendation engine enabled in configuration")

# Create recommendation engine template
recommendation_html = '''{% extends "base.html" %}

{% block title %}Loan Recommendations | {{ config.app.name }}{% endblock %}

{% block header %}Loan Recommendation Engine{% endblock %}
{% block subheader %}Find the optimal loan terms for your financial situation{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-12 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Your Personalized Loan Recommendations</h5>
            </div>
            <div class="card-body">
                <p class="lead">Based on your financial profile and our predictive models, we've identified the following loan options that maximize your approval chances while minimizing costs.</p>
                
                {% if recommendations %}
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead class="table-light">
                                <tr>
                                    <th>Recommendation</th>
                                    <th>Loan Amount</th>
                                    <th>Interest Rate</th>
                                    <th>Term (months)</th>
                                    <th>Monthly Payment</th>
                                    <th>Total Interest</th>
                                    <th>Approval Probability</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for rec in recommendations %}
                                <tr>
                                    <td><span class="badge bg-{{ rec.badge_color }}">{{ rec.label }}</span></td>
                                    <td>${{ rec.loan_amount|format_number }}</td>
                                    <td>{{ rec.interest_rate }}%</td>
                                    <td>{{ rec.term }}</td>
                                    <td>${{ rec.monthly_payment|format_number }}</td>
                                    <td>${{ rec.total_interest|format_number }}</td>
                                    <td>
                                        <div class="progress">
                                            <div class="progress-bar bg-{{ rec.probability_color }}" role="progressbar" style="width: {{ rec.approval_probability }}%;" aria-valuenow="{{ rec.approval_probability }}" aria-valuemin="0" aria-valuemax="100">{{ rec.approval_probability }}%</div>
                                        </div>
                                    </td>
                                    <td>
                                        <a href="{{ url_for('apply_recommendation', rec_id=rec.id) }}" class="btn btn-sm btn-primary">Apply Now</a>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <div class="alert alert-info">
                        <p>To receive personalized loan recommendations, please complete your financial profile or submit a loan application.</p>
                        <a href="{{ url_for('index') }}" class="btn btn-primary">Start Application</a>
                    </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

{% if recommendations %}
<div class="row">
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Monthly Payment Comparison</h5>
            </div>
            <div class="card-body">
                <canvas id="payment-comparison-chart" height="300"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Total Interest Comparison</h5>
            </div>
            <div class="card-body">
                <canvas id="interest-comparison-chart" height="300"></canvas>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-12 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">What-If Analysis</h5>
            </div>
            <div class="card-body">
                <p>Adjust the sliders below to see how changes to your loan parameters affect your approval probability and costs.</p>
                
                <div class="row mb-4">
                    <div class="col-md-4">
                        <label for="what-if-amount" class="form-label">Loan Amount: $<span id="amount-value">{{ recommendations[0].loan_amount }}</span></label>
                        <input type="range" class="form-range" id="what-if-amount" min="{{ min_amount }}" max="{{ max_amount }}" step="500" value="{{ recommendations[0].loan_amount }}">
                    </div>
                    <div class="col-md-4">
                        <label for="what-if-rate" class="form-label">Interest Rate: <span id="rate-value">{{ recommendations[0].interest_rate }}</span>%</label>
                        <input type="range" class="form-range" id="what-if-rate" min="{{ min_rate }}" max="{{ max_rate }}" step="0.25" value="{{ recommendations[0].interest_rate }}">
                    </div>
                    <div class="col-md-4">
                        <label for="what-if-term" class="form-label">Term: <span id="term-value">{{ recommendations[0].term }}</span> months</label>
                        <input type="range" class="form-range" id="what-if-term" min="12" max="60" step="12" value="{{ recommendations[0].term }}">
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="card bg-light">
                            <div class="card-body">
                                <h5 class="card-title">Estimated Monthly Payment</h5>
                                <h3 id="what-if-payment" class="text-primary">$<span>{{ recommendations[0].monthly_payment }}</span></h3>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card bg-light">
                            <div class="card-body">
                                <h5 class="card-title">Approval Probability</h5>
                                <div class="progress" style="height: 30px;">
                                    <div id="what-if-probability" class="progress-bar" role="progressbar" style="width: {{ recommendations[0].approval_probability }}%;" aria-valuenow="{{ recommendations[0].approval_probability }}" aria-valuemin="0" aria-valuemax="100">{{ recommendations[0].approval_probability }}%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endif %}
{% endblock %}

{% block scripts %}
{% if recommendations %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Payment Comparison Chart
        var paymentCtx = document.getElementById('payment-comparison-chart').getContext('2d');
        var paymentChart = new Chart(paymentCtx, {
            type: 'bar',
            data: {
                labels: [{% for rec in recommendations %}'{{ rec.label }}',{% endfor %}],
                datasets: [{
                    label: 'Monthly Payment ($)',
                    data: [{% for rec in recommendations %}{{ rec.monthly_payment }},{% endfor %}],
                    backgroundColor: [{% for rec in recommendations %}'{{ rec.chart_color }}',{% endfor %}],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Monthly Payment ($)'
                        }
                    }
                }
            }
        });
        
        // Interest Comparison Chart
        var interestCtx = document.getElementById('interest-comparison-chart').getContext('2d');
        var interestChart = new Chart(interestCtx, {
            type: 'bar',
            data: {
                labels: [{% for rec in recommendations %}'{{ rec.label }}',{% endfor %}],
                datasets: [{
                    label: 'Total Interest ($)',
                    data: [{% for rec in recommendations %}{{ rec.total_interest }},{% endfor %}],
                    backgroundColor: [{% for rec in recommendations %}'{{ rec.chart_color }}',{% endfor %}],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Total Interest ($)'
                        }
                    }
                }
            }
        });
        
        // What-If Analysis
        function calculatePayment(principal, rate, term) {
            rate = rate / 100 / 12;
            return principal * rate * Math.pow(1 + rate, term) / (Math.pow(1 + rate, term) - 1);
        }
        
        function updateWhatIf() {
            var amount = parseFloat(document.getElementById('what-if-amount').value);
            var rate = parseFloat(document.getElementById('what-if-rate').value);
            var term = parseInt(document.getElementById('what-if-term').value);
            
            // Update displayed values
            document.getElementById('amount-value').textContent = amount.toLocaleString();
            document.getElementById('rate-value').textContent = rate.toFixed(2);
            document.getElementById('term-value').textContent = term;
            
            // Calculate monthly payment
            var payment = calculatePayment(amount, rate, term);
            document.getElementById('what-if-payment').querySelector('span').textContent = payment.toFixed(2);
            
            // Calculate approval probability (simplified example)
            var probability = 90 - (amount / {{ max_amount }} * 20) - (rate / {{ max_rate }} * 10) - (term / 60 * 5);
            probability = Math.max(0, Math.min(100, probability));
            
            var probabilityBar = document.getElementById('what-if-probability');
            probabilityBar.style.width = probability + '%';
            probabilityBar.textContent = probability.toFixed(1) + '%';
            
            // Update color based on probability
            if (probability >= 80) {
                probabilityBar.className = 'progress-bar bg-success';
            } else if (probability >= 60) {
                probabilityBar.className = 'progress-bar bg-info';
            } else if (probability >= 40) {
                probabilityBar.className = 'progress-bar bg-warning';
            } else {
                probabilityBar.className = 'progress-bar bg-danger';
            }
        }
        
        // Add event listeners to sliders
        document.getElementById('what-if-amount').addEventListener('input', updateWhatIf);
        document.getElementById('what-if-rate').addEventListener('input', updateWhatIf);
        document.getElementById('what-if-term').addEventListener('input', updateWhatIf);
    });
</script>
{% endif %}
{% endblock %}'''

with open('templates/recommendations.html', 'w') as f:
    f.write(recommendation_html)

print("Created recommendation engine template")

# Create route handler for recommendations in app_enhanced.py
# This is a placeholder - we'll need to update the actual app_enhanced.py file
recommendation_route = '''
@app.route('/recommendations')
def recommendations():
    # Check if recommendation engine is enabled
    if not config['features']['recommendation_engine']['enabled']:
        flash('Recommendation engine is not enabled yet.')
        return redirect(url_for('index'))
    
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id and config['features']['user_accounts']['enabled']:
        flash('Please log in to access personalized recommendations.')
        return redirect(url_for('login'))
    
    # Get user's financial profile
    conn = sqlite3.connect('data/loan_prediction.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute("""
            SELECT * FROM loan_applications 
            WHERE user_id = ? 
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        profile = cursor.fetchone()
    else:
        # For demo purposes, get a sample application
        cursor.execute("""
            SELECT * FROM loan_applications 
            ORDER BY created_at DESC
            LIMIT 1
        """)
        profile = cursor.fetchone()
    
    # Generate recommendations if profile exists
    recommendations = []
    min_amount = 5000
    max_amount = 40000
    min_rate = 5.0
    max_rate = 15.0
    
    if profile:
        profile = dict(profile)
        
        # Load the ensemble model
        model_path = 'models/ensemble_model.pkl'
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            preprocessor = joblib.load('models/preprocessor.pkl')
            
            # Generate recommendations based on user profile
            # 1. Optimal recommendation (balanced)
            optimal_amount = profile.get('loan_amount', 15000)
            optimal_rate = profile.get('interest_rate', 7.5)
            optimal_term = profile.get('term', 36)
            
            # 2. Conservative recommendation (lower amount, shorter term)
            conservative_amount = max(min_amount, optimal_amount * 0.8)
            conservative_rate = max(min_rate, optimal_rate - 0.5)
            conservative_term = 24
            
            # 3. Aggressive recommendation (higher amount, longer term)
            aggressive_amount = min(max_amount, optimal_amount * 1.2)
            aggressive_rate = min(max_rate, optimal_rate + 1.0)
            aggressive_term = 60
            
            # Calculate monthly payments and total interest
            def calculate_payment(principal, rate, term):
                monthly_rate = rate / 100 / 12
                return principal * monthly_rate * (1 + monthly_rate) ** term / ((1 + monthly_rate) ** term - 1)
            
            def calculate_total_interest(principal, monthly_payment, term):
                return monthly_payment * term - principal
            
            # Calculate approval probabilities using the model
            # This is a simplified example - in a real implementation, we would use the model to predict probabilities
            def calculate_approval_probability(amount
(Content truncated due to size limit. Use line ranges to read in chunks)