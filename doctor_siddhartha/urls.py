from django.urls import path
from django.views.generic import TemplateView

app_name = 'doctor_siddhartha'

urlpatterns = [
    path('dashboard/', TemplateView.as_view(template_name='doctor_dashboard.html'), name='dashboard'),
    path('schedule/', TemplateView.as_view(template_name='schedule.html'), name='schedule'),
    path('patients/', TemplateView.as_view(template_name='patients_records.html'), name='patients'),
    path('prescriptions/', TemplateView.as_view(template_name='prescription.html'), name='prescriptions'),
]