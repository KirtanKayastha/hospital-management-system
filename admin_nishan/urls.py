from django.urls import path
from . import views

urlpatterns = [
    path("", views.admin_dashboard, name="admin_dashboard"),
    path("patients/", views.admin_manage_patients, name="admin_manage_patients"),
    path("doctor/", views.admin_manage_doctor, name="admin_manage_doctor"),
    path("appointments/", views.admin_appointments, name="admin_appointments"),
    path("accounts/", views.admin_accounts, name="admin_accounts"),
    path("reports/", views.admin_reports, name="admin_reports"),
]