# core/celery.py

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()


# start redis server with the command:
# docker run -p 6379:6379 redis
# it will run redis server at localhost:6379 by default.
# if redis image not previously downloaded, it will download first.

# start celery with the command from project root directory:
# celery -A core worker -l info --pool=solo     #if windows
# celery -A core worker -l info  #if linux/mac

# Important: 
# apps folder must contain empty __init__.py.
# Also, core/__init__.py 
# Also all apps must have __init__.py with