from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Auth routes (from auth_kirtan/urls.py)
    path('', include('auth_kirtan.urls')),
    
    # Admin routes (Nishan)
    path('admin-panel/', include('admin_nishan.urls')),
    
    # Doctor routes (Siddhartha)
    path('doctor/', include('doctor_siddhartha.urls')),
    
    # Patient routes (Roshan)
    path('patient/', include('patient_roshan.urls')),
]