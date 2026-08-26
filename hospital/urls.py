from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from hospital.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),

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
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
