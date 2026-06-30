from django.contrib import admin
from django.urls import path, include  # ← ADD 'include' here
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Auth routes (Kirtan)
    path('login/', TemplateView.as_view(template_name='auth_kirtan/login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='auth_kirtan/register.html'), name='register'),
    path('forgot-password/', TemplateView.as_view(template_name='auth_kirtan/forgot_password.html'), name='forgot_password'),
    
    # Admin routes (Nishan)
    path('admin-panel/', include('admin_nishan.urls')),

    # Doctor routes (Siddhartha)
    path('doctor/', include('doctor_siddhartha.urls')),

    # Patient routes (Roshan)
    path('patient/', include('patient_roshan.urls')),
]