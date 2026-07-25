from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.db import connection

def db_check(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
    return HttpResponse(f"✅ Connected to database: {db_name[0]}")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('db-check/', db_check),  # ⬅️ ADD THIS LINE
    
    # Home page (root URL)
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Auth routes (login, register, logout)
    path('', include('auth_kirtan.urls')),
    
    # Patient module
    path('patient/', include('patient_roshan.urls')),
    
    # Doctor module
    path('doctor/', include('doctor_siddhartha.urls')),
    
    # Admin module
    path('admin-panel/', include('admin_nishan.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)