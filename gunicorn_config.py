# Gunicorn configuration for Parking Management System
bind = "0.0.0.0:10000"
workers = 2
timeout = 120
worker_class = "sync"
preload_app = True 