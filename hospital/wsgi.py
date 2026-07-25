"""
WSGI config for hospital project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')

# Ensure DATABASE_URL is available to settings.py during WSGI load
database_url = os.environ.get('DATABASE_URL')
if database_url:
    print(f"🔍 [WSGI] DATABASE_URL detected: {database_url.split('://')[0] if '://' in database_url else 'unknown'}://...")
else:
    print("🔍 [WSGI] WARNING: DATABASE_URL is NOT set in environment!")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
