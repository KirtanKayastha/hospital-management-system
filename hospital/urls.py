from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('auth_kirtan.urls', namespace='auth_kirtan')),
    path('patient/', include('patient_roshan.urls', namespace='patient_roshan')),
]