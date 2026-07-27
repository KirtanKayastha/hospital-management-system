from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # Auth routes (Kirtan)
    path('', include('auth_kirtan.urls', namespace='auth_kirtan')),

    # Admin routes (Nishan)
    path('admin-panel/', include('admin_nishan.urls', namespace='admin_nishan')),

    # Patient routes (Roshan)
    path('patient/', include('patient_roshan.urls', namespace='patient_roshan')),

    # Doctor routes (Siddhartha)
    path('doctor/', include('doctor_siddhartha.urls', namespace='doctor_siddhartha')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)