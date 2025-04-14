import os
import json
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

print("Starting implementation of financial health dashboard...")

# Load configuration
with open('config/config.json', 'r') as f:
    config = json.load(f)

# Update configuration to enable dashboard feature
config['features']['dashboard']['enabled'] = True
with open('config/config.json', 'w') as f:
    json.dump(config, f, indent=4)

print("Dashboard feature enabled in configuration")

# Create dashboard template
dashboard_html = '''{% extends "base.html" %}

{% block title %}Financial Dashboard | {{ config.app.name }}{% endblock %}

{% block header %}Financial Health Dashboard{% endblock %}
{% block subheader %}Comprehensive analysis of your loan applications and financial metrics{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-12 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Financial Overview</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h6 class="text-muted">Total Applications</h6>
                                <h2 id="total-applications">{{ applications|length }}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h6 class="text-muted">Approval Rate</h6>
                                <h2 id="approval-rate">{{ approval_rate|default('N/A') }}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h6 class="text-muted">Average Loan Amount</h6>
                                <h2 id="avg-loan-amount">${{ avg_loan_amount|default('N/A') }}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <h6 class="text-muted">Average Interest Rate</h6>
                                <h2 id="avg-interest-rate">{{ avg_interest_rate|default('N/A') }}%</h2>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Loan Status Distribution</h5>
            </div>
            <div class="card-body">
                <canvas id="loan-status-chart" height="250"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Loan Amount Distribution</h5>
            </div>
            <div class="card-body">
                <canvas id="loan-amount-chart" height="250"></canvas>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-12 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Financial Health Score</h5>
            </div>
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-4">
                        <div class="text-center mb-3">
                            <h1 id="financial-health-score">{{ financial_health_score|default('N/A') }}</h1>
                            <p class="text-muted">Your Financial Health Score</p>
                        </div>
                        <div class="progress" style="height: 25px;">
                            <div class="progress-bar bg-{{ financial_health_color|default('secondary') }}" role="progressbar" style="width: {{ financial_health_percentage|default(0) }}%;" aria-valuenow="{{ financial_health_percentage|default(0) }}" aria-valuemin="0" aria-valuemax="100">{{ financial_health_percentage|default(0) }}%</div>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <canvas id="financial-metrics-radar" height="250"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Recent Loan Applications</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Loan Amount</th>
                                <th>Interest Rate</th>
                                <th>Term</th>
                                <th>Grade</th>
                                <th>Prediction</th>
                                <th>Probability</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for app in applications %}
                            <tr>
                                <td>{{ app.created_at|default('N/A') }}</td>
                                <td>${{ app.loan_amount|default('N/A') }}</td>
                                <td>{{ app.interest_rate|default('N/A') }}%</td>
                                <td>{{ app.term|default('N/A') }} months</td>
                                <td>{{ app.grade|default('N/A') }}</td>
                                <td>
                                    {% if app.predictions and app.predictions|length > 0 %}
                                        {% if app.predictions[0].prediction == 'Stand-standing' %}
                                            <span class="badge bg-success">Good Standing</span>
                                        {% else %}
                                            <span class="badge bg-danger">Default Risk</span>
                                        {% endif %}
                                    {% else %}
                                        <span class="badge bg-secondary">Unknown</span>
                                    {% endif %}
                                </td>
                                <td>
                                    {% if app.predictions and app.predictions|length > 0 %}
                                        {{ (app.predictions[0].probability * 100)|round(2) }}%
                                    {% else %}
                                        N/A
                                    {% endif %}
                                </td>
                                <td>
                                    <a href="{{ url_for('report', application_id=app.id) }}" class="btn btn-sm btn-primary">View Report</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Loan Status Distribution Chart
        var loanStatusCtx = document.getElementById('loan-status-chart').getContext('2d');
        var loanStatusChart = new Chart(loanStatusCtx, {
            type: 'pie',
            data: {
                labels: ['Good Standing', 'Default Risk'],
                datasets: [{
                    data: [{{ good_standing_count|default(0) }}, {{ default_risk_count|default(0) }}],
                    backgroundColor: ['#28a745', '#dc3545'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Loan Amount Distribution Chart
        var loanAmountCtx = document.getElementById('loan-amount-chart').getContext('2d');
        var loanAmountChart = new Chart(loanAmountCtx, {
            type: 'bar',
            data: {
                labels: {{ loan_amount_bins|tojson }},
                datasets: [{
                    label: 'Number of Loans',
                    data: {{ loan_amount_counts|tojson }},
                    backgroundColor: '#4e73df',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Financial Metrics Radar Chart
        var financialMetricsCtx = document.getElementById('financial-metrics-radar').getContext('2d');
        var financialMetricsChart = new Chart(financialMetricsCtx, {
            type: 'radar',
            data: {
                labels: ['Income', 'Credit Score', 'Debt-to-Income', 'Payment History', 'Credit Utilization'],
                datasets: [{
                    label: 'Your Metrics',
                    data: {{ financial_metrics|tojson }},
                    backgroundColor: 'rgba(78, 115, 223, 0.2)',
                    borderColor: '#4e73df',
                    pointBackgroundColor: '#4e73df',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#4e73df'
                }, {
                    label: 'Average Metrics',
                    data: {{ avg_financial_metrics|tojson }},
                    backgroundColor: 'rgba(40, 167, 69, 0.2)',
                    borderColor: '#28a745',
                    pointBackgroundColor: '#28a745',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#28a745'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                }
            }
        });
    });
</script>
{% endblock %}'''

with open('templates/dashboard.html', 'w') as f:
    f.write(dashboard_html)

print("Created dashboard template")

# Create route handler for dashboard in app_enhanced.py
# This is a placeholder - we'll need to update the actual app_enhanced.py file
dashboard_route = '''
@app.route('/dashboard')
def dashboard():
    # Check if dashboard feature is enabled
    if not config['features']['dashboard']['enabled']:
        flash('Dashboard feature is not enabled yet.')
        return redirect(url_for('index'))
    
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id and config['features']['user_accounts']['enabled']:
        flash('Please log in to access the dashboard.')
        return redirect(url_for('login'))
    
    # Get user's applications
    conn = sqlite3.connect('data/loan_prediction.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute("""
            SELECT * FROM loan_applications 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user_id,))
    else:
        # For demo purposes, get all applications
        cursor.execute("""
            SELECT * FROM loan_applications 
            ORDER BY created_at DESC
            LIMIT 10
        """)
    
    applications = [dict(row) for row in cursor.fetchall()]
    
    # Get predictions for each application
    for app in applications:
        cursor.execute("""
            SELECT * FROM predictions
            WHERE application_id = ?
            ORDER BY created_at DESC
        """, (app['id'],))
        
        app['predictions'] = [dict(row) for row in cursor.fetchall()]
    
    # Calculate dashboard metrics
    loan_amounts = [app['loan_amount'] for app in applications if 'loan_amount' in app]
    interest_rates = [app['interest_rate'] for app in applications if 'interest_rate' in app]
    
    # Count good standing vs default risk predictions
    good_standing_count = 0
    default_risk_count = 0
    for app in applications:
        if app['predictions'] and len(app['predictions']) > 0:
            if app['predictions'][0]['prediction'] == 'Stand-standing':
                good_standing_count += 1
            else:
                default_risk_count += 1
    
    # Calculate approval rate
    total_applications = len(applications)
    approval_rate = f"{(good_standing_count / total_applications * 100):.1f}%" if total_applications > 0 else "N/A"
    
    # Calculate average loan amount and interest rate
    avg_loan_amount = f"{sum(loan_amounts) / len(loan_amounts):,.2f}" if loan_amounts else "N/A"
    avg_interest_rate = f"{sum(interest_rates) / len(interest_rates):.2f}" if interest_rates else "N/A"
    
    # Create loan amount bins for histogram
    if loan_amounts:
        min_amount = min(loan_amounts)
        max_amount = max(loan_amounts)
        bin_width = (max_amount - min_amount) / 5
        loan_amount_bins = [f"${int(min_amount + i * bin_width):,} - ${int(min_amount + (i+1) * bin_width):,}" for i in range(5)]
        
        # Count loans in each bin
        loan_amount_counts = [0] * 5
        for amount in loan_amounts:
            bin_index = min(int((amount - min_amount) / bin_width), 4)
            loan_amount_counts[bin_index] += 1
    else:
        loan_amount_bins = []
        loan_amount_counts = []
    
    # Calculate financial health score (simplified example)
    # In a real implementation, this would use more sophisticated metrics
    financial_health_score = 0
    financial_health_percentage = 0
    financial_health_color = "secondary"
    financial_metrics = [0, 0, 0, 0, 0]
    avg_financial_metrics = [70, 65, 60, 75, 68]
    
    if applications:
        # Example calculation based on available data
        # Income score (based on annual_income)
        income_scores = [min(app.get('annual_income', 0) / 100000 * 100, 100) for app in applications]
        income_score = sum(income_scores) / len(income_scores) if income_scores else 0
        
        # Debt-to-Income score (lower is better, so invert)
        dti_scores = [max(100 - app.get('debt_to_income', 0) * 2, 0) for app in applications]
        dti_score = sum(dti_scores) / len(dti_scores) if dti_scores else 0
        
        # Payment history score (based on paid_principal / paid_total)
        payment_scores = []
        for app in applications:
            paid_total = app.get('paid_total', 0)
            paid_principal = app.get('paid_principal', 0)
            if paid_total > 0:
                payment_scores.append(min(paid_principal / paid_total * 100, 100))
        payment_score = sum(payment_scores) / len(paymen
(Content truncated due to size limit. Use line ranges to read in chunks)