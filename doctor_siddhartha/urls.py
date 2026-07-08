from django.urls import path
from . import views

app_name = 'doctor'   # namespace, so your route names don't clash with teammates' apps

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('schedule/', views.schedule, name='schedule'),
    path('patients/', views.patients_list, name='patients_list'),
    path('prescriptions/', views.prescriptions, name='prescriptions'),
    path('prescriptions/<int:patient_id>/', views.prescriptions, name='prescriptions'),
]