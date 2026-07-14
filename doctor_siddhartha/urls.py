from django.urls import path

from . import views

app_name = 'doctor_siddhartha'

urlpatterns = [
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('schedule/', views.schedule, name='schedule'),
    path('patients/', views.patients_records, name='patients'),
    path('prescriptions/', views.prescription, name='prescriptions'),
    path('appointments/approve/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('appointments/reject/<int:appointment_id>/', views.reject_appointment, name='reject_appointment'),
]