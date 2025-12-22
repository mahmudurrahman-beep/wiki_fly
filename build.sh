#!/bin/bash
echo "=== Starting Build Process ==="

# Install dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if not exists (optional)
echo "Checking for superuser..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wiki.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "=== Build Complete ==="
