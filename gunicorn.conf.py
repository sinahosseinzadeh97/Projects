#!/usr/bin/env python3
# Gunicorn configuration file for Loan Prediction Application

# Bind to 0.0.0.0:5000
bind = "0.0.0.0:5000"

# Number of worker processes
workers = 3

# Worker class
worker_class = "sync"

# Timeout in seconds
timeout = 60

# Log level
loglevel = "info"

# Access log file
accesslog = "logs/gunicorn_access.log"

# Error log file
errorlog = "logs/gunicorn_error.log"

# Process name
proc_name = "loan_prediction_app"

# Preload application
preload_app = True

# Daemon mode
daemon = False
