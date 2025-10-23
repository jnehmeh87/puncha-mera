#!/bin/sh

python manage.py migrate
gunicorn --bind :$PORT --workers 3 puncha_mera.wsgi:application
