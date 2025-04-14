// Main JavaScript for Loan Prediction System
const API_URL = 'https://loan-prediction-system-app-aced6d215e0a.herokuapp.com/api';

document.addEventListener('DOMContentLoaded', function() {
    console.log('Loan Prediction System Initialized');
    
    // Form validation and submission
    const predictionForm = document.querySelector('form');
    
    if (predictionForm) {
        predictionForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            let isValid = true;
            const numericInputs = document.querySelectorAll('input[type="number"]');
            
            numericInputs.forEach(input => {
                const value = parseFloat(input.value);
                
                if (isNaN(value)) {
                    isValid = false;
                    input.classList.add('error');
                } else {
                    input.classList.remove('error');
                }
                
                // Check min/max
                const min = parseFloat(input.getAttribute('min'));
                const max = parseFloat(input.getAttribute('max'));
                
                if (!isNaN(min) && value < min) {
                    isValid = false;
                    input.classList.add('error');
                }
                
                if (!isNaN(max) && value > max) {
                    isValid = false;
                    input.classList.add('error');
                }
            });
            
            if (!isValid) {
                alert('Please correct the highlighted fields before submitting.');
                return;
            }
            
            // Prepare form data
            const formData = {
                creditScore: document.getElementById('credit_score').value,
                income: document.getElementById('annual_income').value,
                loanAmount: document.getElementById('loan_amount').value,
                loanTerm: document.getElementById('term').value,
                employmentLength: document.getElementById('emp_length').value
            };
            
            try {
                // Show loading state
                const submitButton = predictionForm.querySelector('button[type="submit"]');
                submitButton.disabled = true;
                submitButton.textContent = 'Predicting...';
                
                // Make API call
                const response = await fetch(`${API_URL}/predict`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    // Show prediction result
                    window.location.href = `/result.html?prediction=${result.prediction}`;
                } else {
                    alert('Error: ' + result.message);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while making the prediction. Please try again.');
            } finally {
                // Reset button state
                const submitButton = predictionForm.querySelector('button[type="submit"]');
                submitButton.disabled = false;
                submitButton.textContent = 'Predict Loan Performance';
            }
        });
    }
    
    // Show/hide sections based on prediction result
    const predictionResult = document.querySelector('.results-container h3 span');
    
    if (predictionResult) {
        const resultValue = predictionResult.textContent.trim();
        const additionalInfo = document.getElementById('additional-info');
        
        if (additionalInfo) {
            if (resultValue === 'Good Standing') {
                additionalInfo.classList.remove('hidden');
            } else {
                additionalInfo.classList.add('hidden');
            }
        }
    }
    
    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    if (tabButtons.length && tabPanes.length) {
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Remove active class from all buttons and panes
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabPanes.forEach(pane => pane.classList.remove('active'));
                
                // Add active class to clicked button and corresponding pane
                button.classList.add('active');
                const target = button.getAttribute('data-target');
                document.getElementById(target).classList.add('active');
            });
        });
    }
}); 