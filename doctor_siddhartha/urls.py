from django.urls import path

from . import views

app_name = 'doctor_siddhartha'

urlpatterns = [
    path('dashboard/', views.doctor_dashboard, name='dashboard'),
    path('schedule/', views.schedule, name='schedule'),
    path('patients/', views.patients_records, name='patients'),
    path('prescriptions/', views.prescription, name='prescriptions'),
]