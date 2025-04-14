// Function to generate personalized PDF report
function generatePersonalizedReport() {
    // Get form data
    const formData = new FormData(document.getElementById('loanForm'));
    
    // Get prediction result
    const result = predictLoanStatus(formData);
    
    // Create PDF document content
    const reportContent = `
    <html>
    <head>
        <title>Loan Application Assessment Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #4e73df;
                padding-bottom: 10px;
            }
            .section {
                margin-bottom: 20px;
            }
            .section-title {
                background-color: #f8f9fa;
                padding: 10px;
                border-left: 4px solid #4e73df;
            }
            .result-box {
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: center;
            }
            .result-approved {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .result-rejected {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            .factor {
                margin-bottom: 10px;
            }
            .factor-positive {
                color: #155724;
            }
            .factor-negative {
                color: #721c24;
            }
            .factor-neutral {
                color: #856404;
            }
            .recommendations {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
            }
            .footer {
                margin-top: 30px;
                text-align: center;
                font-size: 0.8em;
                color: #6c757d;
                border-top: 1px solid #ddd;
                padding-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Loan Application Assessment Report</h1>
            <p>Generated on: ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}</p>
        </div>
        
        <div class="section">
            <h2 class="section-title">Applicant Information</h2>
            <table>
                <tr>
                    <th>Loan Amount</th>
                    <td>$${formData.get('loan_amount')}</td>
                    <th>Interest Rate</th>
                    <td>${formData.get('interest_rate')}%</td>
                </tr>
                <tr>
                    <th>Term</th>
                    <td>${formData.get('term')} months</td>
                    <th>Grade</th>
                    <td>${formData.get('grade')}</td>
                </tr>
                <tr>
                    <th>Employment Length</th>
                    <td>${formData.get('emp_length')} years</td>
                    <th>Annual Income</th>
                    <td>$${formData.get('annual_income')}</td>
                </tr>
                <tr>
                    <th>Debt-to-Income Ratio</th>
                    <td>${formData.get('debt_to_income')}%</td>
                    <th>Income Verification</th>
                    <td>${formData.get('verified_income')}</td>
                </tr>
                <tr>
                    <th>Home Ownership</th>
                    <td>${formData.get('homeownership')}</td>
                    <th>Total Credit Lines</th>
                    <td>${formData.get('total_credit_lines')}</td>
                </tr>
                <tr>
                    <th>Open Credit Lines</th>
                    <td>${formData.get('open_credit_lines')}</td>
                    <th>Number of Mortgage Accounts</th>
                    <td>${formData.get('num_mort_accounts')}</td>
                </tr>
                <tr>
                    <th>Paid Principal</th>
                    <td>$${formData.get('paid_principal')}</td>
                    <th>Paid Total</th>
                    <td>$${formData.get('paid_total')}</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2 class="section-title">Assessment Result</h2>
            <div class="result-box ${result.prediction === 'Stand-standing' ? 'result-approved' : 'result-rejected'}">
                <h2>Loan Status: ${result.prediction === 'Stand-standing' ? 'Good Standing' : 'Default Risk'}</h2>
                <p>${result.prediction === 'Stand-standing' ? 
                    'Based on our analysis, this loan application is predicted to maintain good standing.' : 
                    'Based on our analysis, this loan application has a risk of default.'}</p>
                <p>Confidence: ${(result.probability * 100).toFixed(2)}%</p>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">Key Factors Influencing This Assessment</h2>
            
            ${generateKeyFactors(formData, result)}
        </div>
        
        <div class="section">
            <h2 class="section-title">Recommendations</h2>
            <div class="recommendations">
                ${generateRecommendations(formData, result)}
            </div>
        </div>
        
        <div class="footer">
            <p>This report was generated by the Loan Prediction System using machine learning algorithms.</p>
            <p>The assessment is based on historical lending data and should be used as one of many factors in the loan decision process.</p>
            <p>© ${new Date().getFullYear()} Loan Prediction System</p>
        </div>
    </body>
    </html>
    `;
    
    // Create a Blob with the HTML content
    const blob = new Blob([reportContent], { type: 'text/html' });
    
    // Create a link to download the report
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Loan_Application_Assessment_Report.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Function to generate key factors section
function generateKeyFactors(formData, result) {
    const loanAmount = parseFloat(formData.get('loan_amount') || 0);
    const interestRate = parseFloat(formData.get('interest_rate') || 0);
    const debtToIncome = parseFloat(formData.get('debt_to_income') || 0);
    const annualIncome = parseFloat(formData.get('annual_income') || 0);
    const paidPrincipal = parseFloat(formData.get('paid_principal') || 0);
    const paidTotal = parseFloat(formData.get('paid_total') || 0);
    const grade = formData.get('grade') || 'A';
    
    let factors = '<div class="factors">';
    
    // Paid Principal Factor
    const principalRatio = loanAmount > 0 ? paidPrincipal / loanAmount : 0;
    if (principalRatio >= 0.5) {
        factors += `<div class="factor factor-positive">
            <strong>Paid Principal:</strong> $${paidPrincipal} (${(principalRatio * 100).toFixed(1)}% of loan amount)
            <p>You have paid a significant portion of the principal, which strongly indicates ability to repay.</p>
        </div>`;
    } else if (principalRatio >= 0.3) {
        factors += `<div class="factor factor-neutral">
            <strong>Paid Principal:</strong> $${paidPrincipal} (${(principalRatio * 100).toFixed(1)}% of loan amount)
            <p>You have made moderate progress on principal repayment.</p>
        </div>`;
    } else {
        factors += `<div class="factor factor-negative">
            <strong>Paid Principal:</strong> $${paidPrincipal} (${(principalRatio * 100).toFixed(1)}% of loan amount)
            <p>The amount of principal paid is relatively low compared to the loan amount.</p>
        </div>`;
    }
    
    // Interest Rate Factor
    if (interestRate <= 7) {
        factors += `<div class="factor factor-positive">
            <strong>Interest Rate:</strong> ${interestRate}%
            <p>Your interest rate is low, which reduces the overall cost of the loan and default risk.</p>
        </div>`;
    } else if (interestRate <= 15) {
        factors += `<div class="factor factor-neutral">
            <strong>Interest Rate:</strong> ${interestRate}%
            <p>Your interest rate is moderate, which is typical for this type of loan.</p>
        </div>`;
    } else {
        factors += `<div class="factor factor-negative">
            <strong>Interest Rate:</strong> ${interestRate}%
            <p>Your interest rate is high, which increases the overall cost of the loan and default risk.</p>
        </div>`;
    }
    
    // Debt-to-Income Ratio Factor
    if (debtToIncome <= 20) {
        factors += `<div class="factor factor-positive">
            <strong>Debt-to-Income Ratio:</strong> ${debtToIncome}%
            <p>Your debt-to-income ratio is low, indicating strong financial capacity to take on additional debt.</p>
        </div>`;
    } else if (debtToIncome <= 36) {
        factors += `<div class="factor factor-neutral">
            <strong>Debt-to-Income Ratio:</strong> ${debtToIncome}%
            <p>Your debt-to-income ratio is within acceptable range for most lenders.</p>
        </div>`;
    } else {
        factors += `<div class="factor factor-negative">
            <strong>Debt-to-Income Ratio:</strong> ${debtToIncome}%
            <p>Your debt-to-income ratio is high, which may limit your ability to take on additional debt.</p>
        </div>`;
    }
    
    // Annual Income Factor
    if (annualIncome >= 100000) {
        factors += `<div class="factor factor-positive">
            <strong>Annual Income:</strong> $${annualIncome}
            <p>Your annual income is high, which indicates strong ability to repay the loan.</p>
        </div>`;
    } else if (annualIncome >= 50000) {
        factors += `<div class="factor factor-neutral">
            <strong>Annual Income:</strong> $${annualIncome}
            <p>Your annual income is moderate, which is generally sufficient for this loan amount.</p>
        </div>`;
    } else {
        factors += `<div class="factor factor-negative">
            <strong>Annual Income:</strong> $${annualIncome}
            <p>Your annual income is relatively low compared to the loan amount, which may increase default risk.</p>
        </div>`;
    }
    
    // Loan Grade Factor
    const gradeMap = { 'A': 'Excellent', 'B': 'Good', 'C': 'Satisfactory', 'D': 'Fair', 'E': 'Poor', 'F': 'Very Poor', 'G': 'Extremely Poor' };
    const gradeQuality = gradeMap[grade] || 'Unknown';
    
    if (['A', 'B'].includes(grade)) {
        factors += `<div class="factor factor-positive">
            <strong>Loan Grade:</strong> ${grade} (${gradeQuality})
            <p>Your loan grade indicates excellent creditworthiness and low default risk.</p>
        </div>`;
    } else if (['C', 'D'].includes(grade)) {
        factors += `<div class="factor factor-neutral">
            <strong>Loan Grade:</strong> ${grade} (${gradeQuality})
            <p>Your loan grade indicates moderate creditworthiness and average default risk.</p>
        </div>`;
    } else {
        factors += `<div class="factor factor-negative">
            <strong>Loan Grade:</strong> ${grade} (${gradeQuality})
            <p>Your loan grade indicates lower creditworthiness and higher default risk.</p>
        </div>`;
    }
    
    factors += '</div>';
    return factors;
}

// Function to generate recommendations
function generateRecommendations(formData, result) {
    const isGoodStanding = result.prediction === 'Stand-standing';
    const debtToIncome = parseFloat(formData.get('debt_to_income') || 0);
    const interestRate = parseFloat(formData.get('interest_rate') || 0);
    const grade = formData.get('grade') || 'A';
    
    let recommendations = '<ul>';
    
    if (isGoodStanding) {
        recommendations += '<li>Based on our analysis, your loan application shows strong indicators for successful repayment.</li>';
        
        if (debtToIncome > 30) {
            recommendations += '<li>Consider reducing your overall debt to improve your debt-to-income ratio, which would further strengthen your financial position.</li>';
        }
        
        if (interestRate > 10) {
            recommendations += '<li>You may want to explore refinancing options in the future to secure a lower interest rate.</li>';
        }
        
        recommendations += '<li>Continue maintaining good payment history on existing debts to further improve your credit profile.</li>';
        recommendations += '<li>Consider setting up automatic payments to ensure timely repayment of this loan.</li>';
    } else {
        recommendations += '<li>Based on our analysis, your loan application shows some risk factors that may lead to repayment difficulties.</li>';
        
        if (debtToIncome > 30) {
            recommendations += '<li><strong>Priority:</strong> Work on reducing your overall debt to improve your debt-to-income ratio before taking on additional debt.</li>';
        }
        
        if (!['A', 'B', 'C'].includes(grade)) {
            recommendations += '<li>Focus on improving your credit score to qualify for better loan terms in the future.</li>';
        }
        
        if (interestRate > 15) {
            recommendations += '<li>The high interest rate significantly increases your repayment burden. Consider applying for a smaller loan amount or improving your credit profile before reapplying.</li>';
        }
        
        recommendations += '<li>Consider creating a detailed budget to ensure you can manage all debt obligations.</li>';
        recommendations += '<li>You may want to explore alternative financing options with more favorable terms.</li>';
    }
    
    recommendations += '</ul>';
    return recommendations;
}

// Add event listener to generate report button
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded, adding report buttons");
    
    // Add a button to the results page
    const resultContainer = document.getElementById('resultContainer');
    if (resultContainer) {
        const newPredictionBtn = document.getElementById('newPredictionBtn');
        if (newPredictionBtn) {
            const resultReportButton = document.createElement('button');
            resultReportButton.id = 'generateReportBtn';
            resultReportButton.className = 'btn btn-secondary';
            resultReportButton.style.marginTop = '10px';
            resultReportButton.style.width = '100%';
            resultReportButton.style.marginBottom = '10px';
            resultReportButton.textContent = 'Generate Detailed PDF Report';
            resultReportButton.onclick = function() {
                // Get form data from the hidden form or recreate it
                const formData = new FormData(document.getElementById('loanForm'));
                if (!formData || formData.entries().next().done) {
                    // If form is empty, recreate it from local storage or other source
                    alert("Please go back and fill the form again to generate a report.");
                    return;
                }
                generatePersonali
(Content truncated due to size limit. Use line ranges to read in chunks)