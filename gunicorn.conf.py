# Gunicorn configuration file
import os

# Server socket
bind = os.getenv('BIND', '0.0.0.0:5006')
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', 4))
worker_class = 'gevent'
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'sise-flask'

# Server mechanics
preload_app = True
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (será configurado pelo reverse proxy)
# keyfile = None
# certfile = None