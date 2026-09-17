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

    username = os.environ.get('ADMIN_USERNAME')
    email = os.environ.get('ADMIN_EMAIL')
    password = os.environ.get('ADMIN_PASSWORD')

    if not username or not email or not password:
        print("[BUILD] ADMIN credentials not set; skipping superuser creation.")
        sys.exit(0)

    if username == 'admin' and password == 'admin12345':
        print(f"[BUILD] Using default admin credentials (not recommended for production)")

    if User.objects.filter(username=username).exists():
        u = User.objects.get(username=username)
        u.set_password(password)
        u.is_staff = True
        u.is_superuser = True
        u.is_active = True
        u.save()
        print(f"[BUILD] Superuser '{username}' password updated and permissions set.")
    else:
        User.objects.create_superuser(username, email, password)
        print(f"[BUILD] Superuser '{username}' created.")

except Exception as e:
    print(f"[BUILD] ERROR creating superuser: {e}")
    traceback.print_exc()
    sys.exit(1)
