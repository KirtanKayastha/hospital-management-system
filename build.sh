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

echo "[BUILD] Creating superuser (if ADMIN_USERNAME is set)..."
if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_EMAIL" ] && [ -n "$ADMIN_PASSWORD" ]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
username = '$ADMIN_USERNAME'
email = '$ADMIN_EMAIL'
password = '$ADMIN_PASSWORD'
if User.objects.filter(username=username).exists():
    u = User.objects.get(username=username)
    u.set_password(password)
    u.is_staff = True
    u.is_superuser = True
    u.is_active = True
    u.save()
    print(f'Superuser \"{username}\" updated.')
else:
    User.objects.create_superuser(username, email, password)
    print(f'Superuser \"{username}\" created.')
"
else
    echo "[BUILD] ADMIN_USERNAME/EMAIL/PASSWORD not set; skipping superuser creation."
fi

echo "[BUILD] Build complete!"