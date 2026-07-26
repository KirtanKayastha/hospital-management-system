from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

# hospital/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
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
=======
    path('', include('auth_kirtan.urls', namespace='auth_kirtan')),
    path('patient/', include('patient_roshan.urls', namespace='patient_roshan')),
    path('doctor/', include('doctor_siddhartha.urls', namespace='doctor_siddhartha')),  # add this
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
>>>>>>> 58641b5 (Fix sidebar sizing, scroll bug, prescriptions, and schedule module)
