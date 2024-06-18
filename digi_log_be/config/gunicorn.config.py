"""Gunicorn *development* config file"""

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "digi_log.wsgi:application"
# The granularity of Error log outputs
loglevel = "debug"
# The number of worker processes for handling requests
workers = 2
# The socket to bind
bind = ":8080"
# Restart workers when code changes (development only!)
reload = True
# Write access and error info to /var/log
# log_file = "/var/log/gunicorn/dev.log"
accesslog = errorlog = "/var/log/gunicorn/dev.log"
# errorlog = "/var/log/gunicorn/dev.log"
# Redirect stdout/stderr to log file
# capture_output = True
# PID file so you can easily fetch process ID
# pidfile = "/var/run/gunicorn/dev.pid"
# Daemonize the Gunicorn process (detach & enter background)
daemon = False


