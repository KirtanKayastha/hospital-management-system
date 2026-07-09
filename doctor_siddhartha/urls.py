from django.urls import path
from . import views

app_name = 'doctor'   # namespace, so your route names don't clash with teammates' apps

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('schedule/', views.schedule, name='schedule'),
    path('appointments/<int:appointment_id>/status/', views.update_appointment_status, name='update_appointment_status'),
    path('patients/', views.patients_list, name='patients_list'),
    path('prescriptions/', views.prescriptions, name='prescriptions'),
    path('prescriptions/<int:patient_id>/', views.prescriptions, name='prescriptions'),
    path('prescriptions/view/<int:prescription_id>/', views.prescription_detail, name='prescription_detail'),
    path('prescriptions/delete/<int:prescription_id>/', views.delete_prescription, name='delete_prescription'),
]