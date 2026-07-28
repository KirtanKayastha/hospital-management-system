from django.urls import path
from . import views

app_name = 'admin_nishan'

urlpatterns = [
    path("", views.admin_dashboard, name="admin_dashboard"),
    path("patients/", views.admin_manage_patients, name="admin_manage_patients"),
    path("doctor/", views.admin_manage_doctor, name="admin_manage_doctor"),
    path("pending-doctors/", views.pending_doctors, name="pending_doctors"),
    path("doctors/approve/<int:doctor_id>/", views.approve_doctor, name="approve_doctor"),
    path("doctors/reject/<int:doctor_id>/", views.reject_doctor, name="reject_doctor"),
    path("appointments/", views.admin_appointments, name="admin_appointments"),
    path("accounts/", views.admin_accounts, name="admin_accounts"),
    path("accounts/delete/<int:user_id>/", views.delete_account, name="delete_account"),
    path("reports/", views.admin_reports, name="admin_reports"),
]