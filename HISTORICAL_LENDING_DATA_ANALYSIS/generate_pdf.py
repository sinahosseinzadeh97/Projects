import os
from weasyprint import HTML, CSS

# Define input and output paths
html_file = '/home/ubuntu/loan_prediction_project/report.html'
pdf_file = '/home/ubuntu/loan_prediction_project/Loan_Prediction_System_Report.pdf'

# Create PDF from HTML
HTML(html_file).write_pdf(pdf_file)

print(f"PDF report created successfully: {pdf_file}")
