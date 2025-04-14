#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p /home/ubuntu/loan_prediction_project/static/css
mkdir -p /home/ubuntu/loan_prediction_project/static/js

# Create a basic CSS file for styling
cat > /home/ubuntu/loan_prediction_project/static/css/styles.css << 'EOF'
/* Main Styles for Loan Prediction System */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

header {
    background-color: #343a40;
    color: white;
    padding: 1rem 2rem;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

header h1 {
    margin-bottom: 0.5rem;
}

nav ul {
    display: flex;
    list-style: none;
}

nav ul li {
    margin-right: 1.5rem;
}

nav ul li a {
    color: #f8f9fa;
    text-decoration: none;
    transition: color 0.3s;
}

nav ul li a:hover {
    color: #17a2b8;
}

main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}

.feature-section {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    padding: 2rem;
    margin-bottom: 2rem;
}

.feature-section h2 {
    color: #343a40;
    margin-bottom: 1.5rem;
    border-bottom: 2px solid #f8f9fa;
    padding-bottom: 0.5rem;
}

.visualization-container {
    margin: 1.5rem 0;
    text-align: center;
}

.visualization-container img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.data-container {
    margin: 1.5rem 0;
}

.data-container h3 {
    margin-bottom: 1rem;
    color: #495057;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
}

table th, table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #dee2e6;
}

table th {
    background-color: #f8f9fa;
    font-weight: 600;
}

table tr:hover {
    background-color: #f8f9fa;
}

.form-container {
    margin: 1.5rem 0;
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 4px;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.form-group input, .form-group select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 1rem;
}

.btn {
    display: inline-block;
    background-color: #17a2b8;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.3s;
}

.btn:hover {
    background-color: #138496;
}

.results-container {
    margin-top: 1.5rem;
    padding: 1.5rem;
    background-color: white;
    border-radius: 4px;
    border-left: 4px solid #17a2b8;
}

.positive {
    color: #28a745;
}

.negative {
    color: #dc3545;
}

.highlight {
    background-color: #fff3cd;
    padding: 0.2rem 0.4rem;
    border-radius: 2px;
}

.tabs {
    margin: 1.5rem 0;
}

.tab-header {
    display: flex;
    border-bottom: 1px solid #dee2e6;
}

.tab-btn {
    padding: 0.75rem 1rem;
    cursor: pointer;
    background-color: #f8f9fa;
    border: 1px solid transparent;
    border-bottom: none;
    margin-right: 0.25rem;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

.tab-btn.active {
    background-color: white;
    border-color: #dee2e6;
    border-bottom-color: white;
    margin-bottom: -1px;
}

.tab-content {
    border: 1px solid #dee2e6;
    border-top: none;
    padding: 1.5rem;
}

.tab-pane {
    display: none;
}

.tab-pane.active {
    display: block;
}

.lender-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-top: 1.5rem;
}

.lender-card {
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 1.5rem;
    background-color: #f8f9fa;
}

.lender-card h4 {
    margin-bottom: 1rem;
    color: #343a40;
}

.lender-details {
    margin-bottom: 1rem;
}

.lender-details p {
    margin-bottom: 0.5rem;
}

.lender-pros-cons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.pros h5, .cons h5 {
    margin-bottom: 0.5rem;
}

.pros h5 {
    color: #28a745;
}

.cons h5 {
    color: #dc3545;
}

.pros ul, .cons ul {
    padding-left: 1.5rem;
}

.progress-bar {
    height: 20px;
    background-color: #e9ecef;
    border-radius: 4px;
    margin: 0.5rem 0 1rem 0;
    overflow: hidden;
}

.progress {
    height: 100%;
    background-color: #17a2b8;
    transition: width 0.3s;
}

.risk-score .progress {
    background-color: #28a745;
}

.application-summary {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 4px;
    margin-bottom: 1.5rem;
}

.summary-details {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.risk-assessment, .recommendations {
    margin-top: 1.5rem;
}

footer {
    text-align: center;
    padding: 2rem;
    background-color: #343a40;
    color: white;
    margin-top: 2rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    nav ul {
        flex-direction: column;
    }
    
    nav ul li {
        margin-right: 0;
        margin-bottom: 0.5rem;
    }
    
    .lender-pros-cons {
        grid-template-columns: 1fr;
    }
    
    .summary-details {
        grid-template-columns: 1fr;
    }
}
EOF

# Create a basic JavaScript file
cat > /home/ubuntu/loan_prediction_project/static/js/script.js << 'EOF'
// Main JavaScript for Loan Prediction System

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Loan Prediction System initialized');
    
    // Initialize tab functionality
    initTabs();
    
    // Add event listeners to forms
    initFormListeners();
});

// Initialize tab functionality
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    
    if (tabButtons.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Remove active class from all buttons and panes
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
                
                // Add active class to clicked button
                button.classList.add('active');
                
                // Show corresponding pane
                const tabId = button.getAttribute('data-tab');
                const tabPane = document.getElementById(tabId);
                if (tabPane) {
                    tabPane.classList.add('active');
                }
            });
        });
    }
}

// Initialize form listeners
function initFormListeners() {
    // Debt profile selector
    const debtProfileSelect = document.getElementById('debt-profile');
    if (debtProfileSelect) {
        debtProfileSelect.addEventListener('change', function() {
            const customInputs = document.getElementById('custom-debt-inputs');
            if (customInputs) {
                if (this.value === 'custom') {
                    customInputs.style.display = 'block';
                } else {
                    customInputs.style.display = 'none';
                }
            }
        });
    }
}

// Format currency values
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(value);
}

// Format percentage values
function formatPercent(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 2
    }).format(value / 100);
}
EOF

# Create a dashboard template to integrate all features
cat > /home/ubuntu/loan_prediction_project/templates/dashboard.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - {{ config.app.name }}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
    <style>
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .dashboard-card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            padding: 1.5rem;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .dashboard-card h3 {
            color: #343a40;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f8f9fa;
        }
        
        .dashboard-card p {
            margin-bottom: 1rem;
            color: #6c757d;
        }
        
        .dashboard-card .btn {
            margin-top: 1rem;
        }
        
        .dashboard-card img {
            max-width: 100%;
            height: auto;
            margin-bottom: 1rem;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <header>
        <h1>Dashboard</h1>
        <nav>
            <ul>
                <li><a href="{{ url_for('index') }}">Home</a></li>
                <li><a href="{{ url_for('dashboard') }}">Dashboard</a></li>
                <li><a href="{{ url_for('about') }}">About</a></li>
                <li><a href="{{ url_for('documentation') }}">Documentation</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section class="feature-section">
            <h2>Loan Prediction System Dashboard</h2>
            <p>Welcome to the enhanced Loan Prediction System dashboard. Explore our advanced analytical features to gain deeper insights into loan performance, risk assessment, and financial planning.</p>
            
            <div class="dashboard-grid">
                <!-- Geographic Analysis Card -->
                <div class="dashboard-card">
                    <h3>Geographic Analysis</h3>
                    <img src="{{ url_for('static', filename='img/geographic/regional_risk_scores.png') }}" alt="Geographic Analysis">
                    <p>Analyze location-based risk assessment, regional economic indicators, and loan performance by geographic region.</p>
                    <a href="{{ url_for('geographic_analysis') }}" class="btn">Explore Geographic Analysis</a>
                </div>
                
                <!-- Time-Based Analysis Card -->
                <div class="dashboard-card">
                    <h3>Time-Based Analysis</h3>
                    <img src="{{ url_for('static', filename='img/time_based/seasonal_loan_trends.png') }}" alt="Time-Based Analysis">
                    <p>Discover seasonal trend detection, loan performance forecasting, and repayment timeline projections.</p>
                    <a href="{{ url_for('time_based_analysis') }}" class="btn">Explore Time-Based Analysis</a>
                </div>
                
                <!-- Competitive Analysis Card -->
                <div class="dashboard-card">
                    <h3>Competitive Analysis</h3>
                    <img src="{{ url_for('static', filename='img/competitive/market_comparison_average_interest_rate.png') }}" alt="Competitive Analysis">
                    <p>Compare loan terms with market averages, benchmark against industry standards, and find alternative lender recommendations.</p>
                    <a href="{{ url_for('competitive_analysis') }}" class="btn">Explore Competitive Analysis</a>
                </div>
                
                <!-- Risk Segmentation Card -->
                <div class="dashboard-card">
                    <h3>Risk Segmentation</h3>
                    <img src="{{ url_for('static', filename='img/risk_segmentation/risk_tier_analysis.png') }}" alt="Risk Segmentation">
                    <p>Explore detailed risk profiles beyond binary approval/denial, tiered risk categorization, and custom scoring models.</p>
                    <a href="{{ url_for('risk_segmentation') }}" class="btn">Explore Risk Segmentation</a>
                </div>
                
                <!-- Financial Planning Card -->
                <div class="dashboard-card">
                    <h3>Financial Planning</h3>
                    <img src="{{ url_for('static', filename='img/financial_planning/net_worth_profile_a.png') }}" alt="Financial Planning">
                    <p>Analyze debt consolidation options, retirement impact assessment, and long-term financial health projections.</p>
                    <a href="{{ url_for('financial_planning') }}" class="btn">Explore Financial Planning</a>
                </div>
                
                <!-- Loan Prediction Card -->
                <div class="dashboard-card">
                    <h3>Loan Prediction</h3>
                    <img src="{{ url_for('static', filename='img/random_forest_feature_importance.png') }}" alt="Loan Prediction">
                    <p>Use our advanced machine learning models to predict loan approval and default probability.</p>
                    <a href="{{ url_for('index') }}" class="btn">Make a Prediction</a>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <p>&copy; {{ config.app.name }} {{ config.app.version }}</p>
    </footer>

    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
EOF

# Run the integrated application
cd /home/ubuntu/loan_prediction_project
python3 app_integrated.py
