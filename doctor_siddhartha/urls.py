from django.urls import path
from . import views

app_name = 'doctor_siddhartha'

urlpatterns = [
    path('dashboard/', views.doctor_dashboard, name='dashboard'),
    path('schedule/', views.schedule, name='schedule'),
    path('schedule/edit/<int:slot_id>/', views.edit_availability, name='edit_availability'),
    path('schedule/delete/<int:slot_id>/', views.delete_availability, name='delete_availability'),
    path('patients/', views.patients_records, name='patients'),
    path('patients/<int:patient_id>/add-record/', views.add_medical_record, name='add_medical_record'),
    path('records/<int:record_id>/edit/', views.edit_medical_record, name='edit_medical_record'),
    path('prescriptions/', views.prescription, name='prescriptions'),
    path('prescriptions/<int:prescription_id>/edit/', views.edit_prescription, name='edit_prescription'),
    path('prescriptions/<int:prescription_id>/delete/', views.delete_prescription, name='delete_prescription'),
    path('appointments/approve/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('appointments/reject/<int:appointment_id>/', views.reject_appointment, name='reject_appointment'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('medical-records/', views.medical_records, name='medical_records'),
    path('lab-reports/', views.lab_reports, name='lab_reports'),
]