#!/usr/bin/env bash
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️ Setting up database..."
python manage.py migrate

echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "📝 Importing wiki entries..."
# First create media/entries directory for your util.py functions
mkdir -p media/entries
python import_entries.py

echo "✅ Build completed!"
