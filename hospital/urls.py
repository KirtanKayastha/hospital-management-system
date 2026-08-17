from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.db import connection
import traceback
import os
import subprocess



def db_check(request):
    db_engine = None
    db_name = None
    db_host = None
    db_url_set = None

    try:
        db_engine = connection.settings_dict.get('ENGINE', 'unknown')
        db_name = connection.settings_dict.get('NAME', 'unknown')
        db_host = connection.settings_dict.get('HOST', 'unknown')
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
    except Exception as e:
        db_name = f"Error: {e}"

    db_url_set = os.environ.get('DATABASE_URL')
    db_url_prefix = db_url_set.split('://')[0] if db_url_set and '://' in db_url_set else None

    html = f"""
    <html><head><title>DB Check</title></head><body style="font-family:sans-serif; padding:20px; background:#f7f9fb;">
    <h1 style="color:#191c1e;">Database Connection Check</h1>
    <table style="border-collapse:collapse; margin-top:20px;">
        <tr><td style="padding:8px 16px; border-bottom:1px solid #c3c6d7;"><strong>Database Engine</strong></td><td style="padding:8px 16px; border-bottom:1px solid #c3c6d7;">{db_engine}</td></tr>
        <tr><td style="padding:8px 16px; border-bottom:1px solid #c3c6d7;"><strong>Database Name</strong></td><td style="padding:8px 16px; border-bottom:1px solid #c3c6d7;">{db_name}</td></tr>
        <tr><td style="padding:8px 16px; border-bottom:1px solid #c3c6d7;"><strong>Database Host</strong></td><td style="padding:8px 16px; border-bottom:1px solid #c3c6d7;">{db_host}</td></tr>
        <tr><td style="padding:8px 16px; border-bottom:1px solid #c3c6d7;"><strong>DATABASE_URL Set</strong></td><td style="padding:8px 16px; border-bottom:1px solid #c3c6d7;">{'Yes' if db_url_set else 'No'}</td></tr>
        <tr><td style="padding:8px 16px;"><strong>DATABASE_URL Prefix</strong></td><td style="padding:8px 16px;">{db_url_prefix or 'N/A'}</td></tr>
        <tr><td style="padding:8px 16px;"><strong>DEBUG Setting</strong></td><td style="padding:8px 16px;">{settings.DEBUG}</td></tr>
    </table>
    </body></html>
    """
    return HttpResponse(html)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('db-check/', db_check),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # Auth routes (Kirtan)
    path('', include('auth_kirtan.urls', namespace='auth_kirtan')),

    # Admin routes (Nishan)
    path('admin-panel/', include('admin_nishan.urls', namespace='admin_nishan')),

    # Patient routes (Roshan)
    path('patient/', include('patient_roshan.urls', namespace='patient_roshan')),

    # Doctor routes (Siddhartha)
    path('doctor/', include('doctor_siddhartha.urls', namespace='doctor_siddhartha')),

    path('privacy-policy/', TemplateView.as_view(template_name='privacy_policy.html'), name='privacy_policy'),
    path('terms/', TemplateView.as_view(template_name='terms_of_service.html'), name='terms_of_service'),
    path('faq/', TemplateView.as_view(template_name='faq.html'), name='faq'),
    path('support/', TemplateView.as_view(template_name='support.html'), name='support'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
