#!/bin/bash
service mongodb restart
gunicorn --bind 0.0.0.0:80 --log-file /data/logs/error_logs.log --access-logfile /data/logs/access_logs.log wsgi:application --timeout 300 --graceful-timeout 300
