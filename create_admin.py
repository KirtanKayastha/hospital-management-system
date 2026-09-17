#!/usr/bin/env python
import os
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')

try:
    import django
    django.setup()
    from django.contrib.auth import get_user_model

    User = get_user_model()

    username = os.environ.get('ADMIN_USERNAME', '')
    email = os.environ.get('ADMIN_EMAIL', '')
    password = os.environ.get('ADMIN_PASSWORD', '')

    print(f"[BUILD] ADMIN_USERNAME={username!r}", file=sys.stderr, flush=True)
    print(f"[BUILD] ADMIN_EMAIL is set: {bool(email)}", file=sys.stderr, flush=True)
    print(f"[BUILD] ADMIN_PASSWORD is set: {bool(password)}", file=sys.stderr, flush=True)

    if not username or not email or not password:
        print("[BUILD] ADMIN credentials not set; skipping superuser creation.", file=sys.stderr, flush=True)
        sys.exit(0)

    existing = User.objects.filter(username=username).first()
    if existing:
        existing.set_password(password)
        existing.is_staff = True
        existing.is_superuser = True
        existing.is_active = True
        existing.save()
        print(f"[BUILD] Superuser '{username}' updated.", file=sys.stderr, flush=True)
    else:
        User.objects.create_superuser(username, email, password)
        print(f"[BUILD] Superuser '{username}' created.", file=sys.stderr, flush=True)

except Exception as e:
    print(f"[BUILD] ERROR creating superuser: {e}", file=sys.stderr, flush=True)
    traceback.print_exc()
    sys.exit(1)
