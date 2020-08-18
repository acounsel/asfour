release: python manage.py migrate
web: python manage.py runserver 0.0.0.0:5000
worker: REMAP_SIGTERM=SIGQUIT celery worker --app asfour.celery.app --loglevel info