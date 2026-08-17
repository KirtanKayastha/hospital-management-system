from django.urls import path
from . import views

app_name = 'admin_nishan'

urlpatterns = [
    path("", views.admin_dashboard, name="admin_dashboard"),
    path("patients/", views.admin_manage_patients, name="admin_manage_patients"),
    path("patients/edit/<int:patient_id>/", views.edit_patient, name="edit_patient"),
    
    path(
    "patients/password/<int:patient_id>/",
    views.change_patient_password,
    name="change_patient_password",
),

path(
    "patients/enable/<int:patient_id>/",
    views.enable_patient,
    name="enable_patient",
),

path(
    "patients/disable/<int:patient_id>/",
    views.disable_patient,
    name="disable_patient",
),

path(
    "patients/delete/<int:patient_id>/",
    views.delete_patient,
    name="delete_patient",
),
    path("doctor/", views.admin_manage_doctor, name="admin_manage_doctor"),
    path("doctor/edit/<int:doctor_id>/", views.edit_doctor, name="edit_doctor"),
    path("doctor/password/<int:doctor_id>/",views.change_doctor_password,name="change_doctor_password"),
    path(
    "doctor/enable/<int:doctor_id>/",
    views.enable_doctor,
    name="enable_doctor",
),
path(
    "doctor/disable/<int:doctor_id>/",
    views.disable_doctor,
    name="disable_doctor",
),
path(
    "doctor/delete/<int:doctor_id>/",
    views.delete_doctor,
    name="delete_doctor",
),
    path("pending-doctors/", views.pending_doctors, name="pending_doctors"),
    path("doctors/approve/<int:doctor_id>/", views.approve_doctor, name="approve_doctor"),
    path("doctors/reject/<int:doctor_id>/", views.reject_doctor, name="reject_doctor"),
    path("appointments/", views.admin_appointments, name="admin_appointments"),
    path("accounts/", views.admin_accounts, name="admin_accounts"),
    path("accounts/delete/<int:user_id>/", views.delete_account, name="delete_account"),
    path("reports/", views.admin_reports, name="admin_reports"),
    path("billing/", views.admin_billing, name="admin_billing"),

path(
    "billing/",
    views.admin_billing,
    name="admin_billing"
), 


path(
    "billing/create-invoice/",
    views.create_invoice,
    name="create_invoice"
),

path('billing/edit/<int:invoice_id>/', views.edit_invoice, name='edit_invoice'),
path('billing/print/<int:invoice_id>/', views.print_invoice, name='print_invoice'),
path('billing/delete/<int:invoice_id>/', views.delete_invoice, name='delete_invoice'),


]