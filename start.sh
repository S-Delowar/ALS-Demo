#!/bin/sh

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Creating superuser if not exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin', 
        email='admin@mail.com', 
        password='admin123'
    )
"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --timeout 120
