#! /bin/bash

gunicorn server.wsgi --log-file - &
python manage.py celery worker --loglevel=INFO -c3
