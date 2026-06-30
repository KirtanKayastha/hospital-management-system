from django.urls import path
from django.views.generic import TemplateView

app_name = 'doctor_siddhartha'

urlpatterns = [
    path('dashboard/', TemplateView.as_view(template_name='doc_siddhartha/doctor_dashboard.html'), name='dashboard'),
    path('schedule/', TemplateView.as_view(template_name='doc_siddhartha/schedule.html'), name='schedule'),
    path('patients/', TemplateView.as_view(template_name='doc_siddhartha/patients_records.html'), name='patients'),
    path('prescriptions/', TemplateView.as_view(template_name='doc_siddhartha/prescription.html'), name='prescriptions'),
]