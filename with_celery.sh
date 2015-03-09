#! /bin/bash

gunicorn server.wsgi --log-file - &
python manage.py celery --log-level=INFO -c3
