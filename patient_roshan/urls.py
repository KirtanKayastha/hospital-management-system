from django.urls import path
from . import views

app_name = 'patient_roshan'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('find-doctor/', views.find_doctor, name='find_doctor'),
    path('appointments/', views.my_appointments, name='my_appointments'),
    path('appointments/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/<int:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    path('records/', views.medical_records, name='medical_records'),
    path('lab-reports/', views.lab_reports, name='lab_reports'),
    path('profile/', views.profile, name='profile'),
    path('profile/emergency-contact/', views.update_emergency_contact, name='update_emergency_contact'),
    path('profile/change-password/', views.change_password, name='change_password'),
path('prescriptions/', views.prescriptions, name='prescriptions'),
path('billing/', views.billing, name='billing'),
path('messages/', views.messages, name='messages'),
path('notifications/', views.notifications, name='notifications'),
path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
path('settings/', views.settings, name='settings'),
]