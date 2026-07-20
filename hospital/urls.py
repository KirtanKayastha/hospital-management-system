from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('auth_kirtan.urls', namespace='auth_kirtan')),
    path('patient/', include('patient_roshan.urls', namespace='patient_roshan')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)