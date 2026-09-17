import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('ADMIN_USERNAME')
email = os.environ.get('ADMIN_EMAIL')
password = os.environ.get('ADMIN_PASSWORD')

if not username or not email or not password:
    print("[BUILD] ADMIN credentials not set; skipping superuser creation.")
    sys.exit(0)

if User.objects.filter(username=username).exists():
    u = User.objects.get(username=username)
    u.set_password(password)
    u.is_staff = True
    u.is_superuser = True
    u.is_active = True
    u.save()
    print(f"Superuser '{username}' updated.")
else:
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created.")
