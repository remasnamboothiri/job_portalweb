# Gunicorn configuration file
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 60  # Increased from default 30 seconds
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "job_platform"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Memory and performance
preload_app = True
worker_tmp_dir = "/dev/shm"

# Graceful timeout for worker shutdown
graceful_timeout = 30

# Environment variables
raw_env = [
    f"DJANGO_SETTINGS_MODULE=job_platform.settings",
]