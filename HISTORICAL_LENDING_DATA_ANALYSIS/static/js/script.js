// Main JavaScript for Loan Prediction System

document.addEventListener('DOMContentLoaded', function() {
    console.log('Loan Prediction System Initialized');
    
    // Form validation
    const predictionForm = document.querySelector('form');
    
    if (predictionForm) {
        predictionForm.addEventListener('submit', function(e) {
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
                e.preventDefault();
                alert('Please correct the highlighted fields before submitting.');
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