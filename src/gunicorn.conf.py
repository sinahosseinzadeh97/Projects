#!/usr/bin/env python3
# Gunicorn configuration file for Loan Prediction Application

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:{}".format(int(os.environ.get("PORT", 5000)))
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'loan_prediction_app'

# SSL
keyfile = None
certfile = None

# Preload application
preload_app = True

# Daemon mode
daemon = False
