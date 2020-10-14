release: python manage.py migrate
web: gunicorn asfour.wsgi —-log-file -
worker: REMAP_SIGTERM=SIGQUIT celery worker --app asfour.celery.app --loglevel info