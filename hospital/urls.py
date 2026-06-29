from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='auth_kirtan/login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='auth_kirtan/register.html'), name='register'),
    path('forgot-password/', TemplateView.as_view(template_name='auth_kirtan/forgot_password.html'), name='forgot_password'),  # ✅ Added auth_kirtan/ prefix
]