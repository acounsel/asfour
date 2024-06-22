release: python manage.py migrate
web: gunicorn asfour.wsgi —-log-file -
worker: REMAP_SIGTERM=SIGQUIT celery --app asfour.celery.app worker --loglevel=info