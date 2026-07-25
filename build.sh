#!/usr/bin/env bash
set -o errexit

echo "🔍 Checking environment variables..."
echo "🔍 DATABASE_URL set: $([ -n "$DATABASE_URL" ] && echo 'Yes' || echo 'No')"
if [ -n "$DATABASE_URL" ]; then
    echo "🔍 DATABASE_URL starts with: $(echo "$DATABASE_URL" | cut -d: -f1)"
fi
echo "🔍 DEBUG: $DEBUG"
echo "🔍 SECRET_KEY set: $([ -n "$SECRET_KEY" ] && echo 'Yes' || echo 'No')"

echo "🔍 Installing dependencies..."
pip install -r requirements.txt

echo "🔍 Collecting static files..."
python manage.py collectstatic --no-input

echo "🔍 Running migrations..."
python manage.py migrate

echo "🔍 Auto-creating superuser..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell

echo "✅ Build complete!"