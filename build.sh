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
    export ADMIN_USERNAME ADMIN_EMAIL ADMIN_PASSWORD
    python create_admin.py
else
    echo "[BUILD] ADMIN_USERNAME/EMAIL/PASSWORD not set; skipping superuser creation."
fi

echo "[BUILD] Build complete!"