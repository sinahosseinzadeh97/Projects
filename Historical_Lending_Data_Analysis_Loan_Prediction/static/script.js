// Main JavaScript for Loan Prediction System
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tabs
    const tabs = document.querySelectorAll('.nav-tabs a');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Hide all tab contents
            tabContents.forEach(content => {
                content.style.display = 'none';
            });
            
            // Show the corresponding tab content
            const targetId = this.getAttribute('href').substring(1);
            document.getElementById(targetId).style.display = 'block';
        });
    });
    
    // Show the first tab by default
    if (tabs.length > 0) {
        tabs[0].click();
    }
    
    // Initialize prediction form
    const predictionForm = document.getElementById('prediction-form');
    if (predictionForm) {
        predictionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            makePrediction();
        });
    }
    
    // Initialize what-if analysis form
    const whatIfForm = document.getElementById('what-if-form');
    if (whatIfForm) {
        whatIfForm.addEventListener('submit', function(e) {
            e.preventDefault();
            performWhatIfAnalysis();
        });
    }
    
    // Initialize PDF report generation button
    const generateReportBtn = document.getElementById('generate-report-btn');
    if (generateReportBtn) {
        generateReportBtn.addEventListener('click', function() {
            generatePDFReport();
        });
    }
});

// Function to make loan prediction
function makePrediction() {
    // Get form values
    const loanAmount = parseFloat(document.getElementById('loan-amount').value);
    const interestRate = parseFloat(document.getElementById('interest-rate').value);
    const term = parseInt(document.getElementById('term').value);
    const grade = document.getElementById('grade').value;
    const empLength = parseFloat(document.getElementById('emp-length').value);
    const annualIncome = parseFloat(document.getElementById('annual-income').value);
    const dti = parseFloat(document.getElementById('dti').value);
    const incomeVerification = document.getElementById('income-verification').value;
    const homeOwnership = document.getElementById('home-ownership').value;
    const totalCreditLines = parseInt(document.getElementById('total-credit-lines').value);
    const openCreditLines = parseInt(document.getElementById('open-credit-lines').value);
    const mortgageAccounts = parseInt(document.getElementById('mortgage-accounts').value);
    const paidPrincipal = parseFloat(document.getElementById('paid-principal').value);
    const paidTotal = parseFloat(document.getElementById('paid-total').value);
    
    // Validate inputs
    if (isNaN(loanAmount) || isNaN(interestRate) || isNaN(term) || isNaN(empLength) || 
        isNaN(annualIncome) || isNaN(dti) || isNaN(totalCreditLines) || 
        isNaN(openCreditLines) || isNaN(mortgageAccounts) || isNaN(paidPrincipal) || 
        isNaN(paidTotal)) {
        showError("Please fill in all required fields with valid numbers.");
        return;
    }
    
    // Calculate prediction using client-side algorithm
    // This is a simplified version of the model's prediction logic
    let predictionScore = 0;
    
    // Factor 1: Loan amount relative to income
    const loanToIncomeRatio = loanAmount / annualIncome;
    if (loanToIncomeRatio < 0.1) {
        predictionScore += 25;
    } else if (loanToIncomeRatio < 0.2) {
        predictionScore += 20;
    } else if (loanToIncomeRatio < 0.3) {
        predictionScore += 15;
    } else if (loanToIncomeRatio < 0.4) {
        predictionScore += 10;
    } else {
        predictionScore += 5;
    }
    
    // Factor 2: Debt-to-income ratio
    if (dti < 10) {
        predictionScore += 25;
    } else if (dti < 20) {
        predictionScore += 20;
    } else if (dti < 30) {
        predictionScore += 15;
    } else if (dti < 40) {
        predictionScore += 10;
    } else {
        predictionScore += 5;
    }
    
    // Factor 3: Credit history (using total credit lines as a proxy)
    if (totalCreditLines > 20) {
        predictionScore += 15;
    } else if (totalCreditLines > 10) {
        predictionScore += 20;
    } else if (totalCreditLines > 5) {
        predictionScore += 15;
    } else {
        predictionScore += 10;
    }
    
    // Factor 4: Employment length
    if (empLength > 10) {
        predictionScore += 15;
    } else if (empLength > 5) {
        predictionScore += 12;
    } else if (empLength > 2) {
        predictionScore += 10;
    } else {
        predictionScore += 5;
    }
    
    // Factor 5: Grade
    switch(grade) {
        case 'A':
            predictionScore += 20;
            break;
        case 'B':
            predictionScore += 16;
            break;
        case 'C':
            predictionScore += 12;
            break;
        case 'D':
            predictionScore += 8;
            break;
        default:
            predictionScore += 4;
    }
    
    // Normalize score to probability (0-100)
    const probability = Math.min(100, Math.max(0, predictionScore));
    const normalizedProbability = probability / 100;
    
    // Determine prediction
    const isPredictionPositive = probability >= 50;
    const predictionResult = isPredictionPositive ? "Good Standing" : "Default Risk";
    
    // Show result
    showPredictionResult(predictionResult, normalizedProbability);
    
    // Show the PDF report generation button
    const reportBtnContainer = document.getElementById('report-btn-container');
    if (reportBtnContainer) {
        reportBtnContainer.style.display = 'block';
    }
    
    // Store form data for report generation
    window.formData = {
        loanAmount,
        interestRate,
        term,
        grade,
        empLength,
        annualIncome,
        dti,
        incomeVerification,
        homeOwnership,
        totalCreditLines,
        openCreditLines,
        mortgageAccounts,
        paidPrincipal,
        paidTotal,
        predictionResult,
        probability: normalizedProbability
    };
}

// Function to show prediction result
function showPredictionResult(prediction, probability) {
    const resultContainer = document.getElementById('result-container');
    const resultTitle = document.getElementById('result-title');
    const resultMessage = document.getElementById('result-message');
    const progressBar = document.getElementById('progress-bar');
    const probabilityValue = document.getElementById('probability-value');
    const thresholdValue = document.getElementById('threshold-value');
    
    // Update result container class
    resultContainer.className = 'result-container';
    resultContainer.classList.add(prediction === 'Good Standing' ? 'result-success' : 'result-danger');
    
    // Update result text
    resultTitle.textContent = `Loan Status: ${prediction}`;
    resultMessage.textContent = `The model predicts this loan will ${prediction === 'Good Standing' ? 'maintain good standing' : 'default'}.`;
    
    // Update progress bar
    const probabilityPercentage = Math.round(probability * 100);
    progressBar.style.width = `${probabilityPercentage}%`;
    probabilityValue.textContent = `${probabilityPercentage}%`;
    thresholdValue.textContent = '50%';
    
    // Show result container
    resultContainer.style.display = 'block';
    
    // Scroll to result
    resultContainer.scrollIntoView({ behavior: 'smooth' });
}

// Function to show error message
function showError(message) {
    alert(message);
}

// Function to perform what-if analysis
function performWhatIfAnalysis() {
    // Get form values
    const loanAmount = parseFloat(document.getElementById('what-if-loan-amount').value);
    const interestRate = parseFloat(document.getElementById('what-if-interest-rate').value);
    const term = parseInt(document.getElementById('what-if-term').value);
    
    // Validate inputs
    if (isNaN(loanAmount) || isNaN(interestRate) || isNaN(term)) {
        showError("Please fill in all required fields with valid numbers.");
        return;
    }
    
    // Calculate monthly payment
    const monthlyInterestRate = interestRate / 100 / 12;
    const monthlyPayment = loanAmount * monthlyInterestRate * Math.pow(1 + monthlyInterestRate, term) / (Math.pow(1 + monthlyInterestRate, term) - 1);
    
    // Calculate total interest
    const totalInterest = (monthlyPayment * term) - loanAmount;
    
    // Calculate approval probability (simplified algorithm)
    let approvalScore = 70; // Base score
    
    // Adjust based on loan amount
    if (loanAmount < 10000) {
        approvalScore += 10;
    } else if (loanAmount > 30000) {
        approvalScore -= 10;
    }
    
    // Adjust based on interest rate
    if (interestRate < 5) {
        approvalScore += 10;
    } else if (interestRate > 10) {
        approvalScore -= 10;
    }
    
    // Adjust based on term
    if (term <= 36) {
        approvalScore += 10;
    } else if (term > 60) {
        approvalScore -= 10;
    }
    
    // Normalize score to probability (0-100)
    const approvalProbability = Math.min(100, Math.max(0, approvalScore));
    
    // Show results
    showWhatIfResults(monthlyPayment, totalInterest, approvalProbability);
}

// Function to show what-if analysis results
function showWhatIfResults(monthlyPayment, totalInterest, approvalProbability) {
    const resultsContainer = document.getElementById('what-if-results');
    
    // Format values
    const formattedMonthlyPayment = monthlyPayment.toFixed(2);
    const formattedTotalInterest = totalInterest.toFixed(2);
    
    // Determine probability color
    let probabilityColor = 'danger';
    if (approvalProbability >= 80) {
        probabilityColor = 'success';
    } else if (approvalProbability >= 60) {
        probabilityColor = 'warning';
    }
    
    // Update results HTML
    resultsContainer.innerHTML = `
        <h3>Analysis Results</h3>
        <div class="dashboard-container">
            <div class="dashboard-card">
                <div class="dashboard-card-header">
                    <h4 class="dashboard-card-title">Monthly Payment</h4>
                </div>
                <div class="dashboard-value">$${formattedMonthlyPayment}</div>
            </div>
            <div class="dashboard-card">
                <div class="dashboard-card-header">
                    <h4 class="dashboard-card-title">Total Interest</h4>
                </div>
                <div class="dashboard-value">$${formattedTotalInterest}</div>
            </div>
            <div class="dashboard-card">
                <div class="dashboard-card-header">
                    <h4 class="dashboard-card-title">Approval Probability</h4>
                </div>
                <div class="dashboard-value text-${probabilityColor}">${approvalProbability}%</div>
            </div>
        </div>
    `;
    
    // Show results container
    resultsContainer.style.display = 'block';
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

// Function to generate PDF report
function generatePDFReport() {
    if (!window.formData) {
        showError("Please make a prediction first.");
        return;
    }
    
    // Create a new jsPDF instance
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    // Set font size and style
    doc.setFontSize(22);
    doc.setFont("helvetica", "bold");
    
    // Add title
    doc.text("Loan Prediction Report", 105, 20, { align: "center" });
    
    // Add date
    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    const today = new Date();
    doc.text(`Generated on: ${today.toLocaleDateString()} ${today.toLocaleTimeString()}`, 105, 30, { align: "center" });
    
    // Add horizontal line
    doc.setDrawColor(200, 200, 200);
    doc.line(20, 35, 190, 35);
    
    // Add prediction result
    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.text("Prediction Result", 20, 45);
    
    doc.setFontSize(14);
    const resultColor = window.formData.predictionResult === "Good Standing" ? [0, 128, 0] : [220, 53, 69];
    doc.setTextColor(resultColor[0], resultColor[1], resultColor[2]);
    doc.text(`Loan Status: ${window.formData.predictionResult}`, 20, 55);
    
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(12);
    doc.setFont("helvetica", "normal");
    doc.text(`Probability: ${Math.round(window.formData.probability * 100)}%`, 20, 65);
    doc.text(`Decision Threshold: 50%`, 20, 75);
    
    // Add loan details
    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.text("Loan Details", 20, 90);
    
    doc.setFontSize(12);
    doc.setFont("helvetica", "normal");
    doc.text(`Loan Amount: $${window.formData.loanAmount.toLocaleString()}`, 20, 100);
    doc.text(`Interest Rate: ${window.formData.interestRate}%`, 20, 110);
    doc.text(`Term: ${window.formData.term} months`, 20, 120);
    doc.text(`Grade: ${window.formData.grade}`, 20, 130);
    
    // Add borrower details
    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.text("Borrower Details", 120, 90);
    
    doc.setFontSize(12);
    doc.setFont("helvetica", "normal");
    doc.text(`Annual Income: $${window.formData.annualIncome.toLocaleString()}`, 120, 100);
    doc.text(`Employment Length: ${window.formData.empLength} years`, 120, 110);
    doc.text(`Debt-to-Income Ratio: ${window.formData.dti}%`, 120, 120);
    doc.text(`Home Ownership: ${window.formData.homeOwnership}`, 120, 130);
    
    // Add key factors
    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.text("Key Factors Influencing Prediction", 20, 150);
    
    doc.setFontSize(12);
    doc.setFont("helvetica", "normal");
    
    // Calculate key factors
    const factors = [];
    
    // Loan to income ratio
    const loanToIncomeRatio = window.formData.loanAmount / window.formData.annualIncome;
    if (loanToIncomeRatio < 0.2) {
        factors.push({
            name: "Loan-to-Income Ratio",
            value: `${(loanToIncomeRatio * 100).toFixed(1)}%`,
            impact: "Positive",
            description: "Your loan amount is low relative to your income, which is favorable."
        });
    } else if (loanToIncomeRatio > 0.4) {
        factors.push({
            name: "Loan-to-Income Ratio",
            value: `${(loanToIncomeRatio * 100).toFixed(1)}%`,
            impact: "Negative",
            description: "Your loan amount is high relative to your income, which increases risk."
        });
    }
    
    // DTI
    if (window.formData.dti < 20) {
        factors.push({
            name: "Debt-to-Income Ratio",
            value: `${window.formData.dti}%`,
            impact: "Positive",
            description: "Your debt-to-income ratio is low, indicating good financial health."
        });
    } else if (window.formData.dti > 35) {
        factors.push({
            name: "Debt-to-Income Ratio",
            value: `${window.formData.dti}%`,
            impact: "Negative",
            description: "Your debt-to-income ratio is high, which may affect your ability to repay."
        });
    }
    
    // Employment length
    if (window.formData.empLength > 5) {
        factors.push({
            name: "Employment Length",
            value: `${window.formData.empLength} years`,
            impact: "Positive",
            description: "Your long employment history indicates stability."
        });
    } else if (window.formData.empLength < 2)
(Content truncated due to size limit. Use line ranges to read in chunks)