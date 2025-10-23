#!/bin/sh

python manage.py migrate
gunicorn --bind :8000 --workers 3 puncha_mera.wsgi:application
