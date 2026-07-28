#!/usr/bin/env bash
set -o errexit

echo "[BUILD] Checking environment variables..."
echo "[BUILD] DATABASE_URL set: $([ -n "$DATABASE_URL" ] && echo "Yes" || echo "No")"
if [ -n "$DATABASE_URL" ]; then
    echo "[BUILD] DATABASE_URL starts with: $(echo "$DATABASE_URL" | cut -d: -f1)"
fi
echo "[BUILD] DEBUG: $DEBUG"
echo "[BUILD] SECRET_KEY set: $([ -n "$SECRET_KEY" ] && echo "Yes" || echo "No")"

echo "[BUILD] Installing dependencies..."
pip install -r requirements.txt

echo "[BUILD] Collecting static files..."
python manage.py collectstatic --no-input

echo "[BUILD] Running migrations..."
python manage.py migrate

echo "[BUILD] Auto-creating superuser (if not exists)..."
echo "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', '[REDACTED EMAIL]', '[REDACTED PASSWORD]')
    print('[SUPERUSER] Created admin user')
else:
    print('[SUPERUSER] Admin user already exists, skipping')
" | python manage.py shell

echo "[BUILD] Build complete!"