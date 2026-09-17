import os
import sys

from django.apps import AppConfig


class AdminNishanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_nishan'

    def ready(self):
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        if not admin_username or not admin_email or not admin_password:
            return
        if 'runserver' not in sys.argv and 'gunicorn' not in sys.argv[0]:
            return
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            if User.objects.filter(username=admin_username).exists():
                u = User.objects.get(username=admin_username)
                u.set_password(admin_password)
                u.is_staff = True
                u.is_superuser = True
                u.is_active = True
                u.save()
            else:
                User.objects.create_superuser(admin_username, admin_email, admin_password)
        except Exception:
            pass