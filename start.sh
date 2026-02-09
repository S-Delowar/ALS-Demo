#!/bin/sh

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Creating superuser if not exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
email = 'admin@mail.com'
password = 'admin123'
profession = 'System Admin'

# Check by EMAIL, not username
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email, 
        password=password,
        profession=profession  # Added this field based on your serializer
    )
    print(f'Superuser {email} created successfully.')
else:
    print(f'Superuser {email} already exists.')
"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Initializing Weaviate Schema..."
python manage.py shell -c "
from apps.memory.schema import create_schema; 
create_schema()"

echo "Starting Gunicorn..."
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --timeout 120
