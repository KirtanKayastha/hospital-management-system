# API / URL Structure

## 1. URL Organization

All application URLs are included in the root `hospital/urls.py` configuration:

```
hospital/urls.py
├── admin/                          # Django Admin Panel
├── auth/                           # Authentication URLs
│   └── auth_kirtan/urls.py
├── patient/                        # Patient Module URLs
│   └── patient_roshan/urls.py
├── doctor/                         # Doctor Module URLs
│   └── doctor_siddhartha/urls.py
└── admin/                          # Admin Module URLs
    └── admin_nishan/urls.py
```

## 2. Authentication URLs

| URL | Method | Access | Description |
|-----|--------|--------|-------------|
| `/auth/login/` | GET/POST | Public | User login form |
| `/auth/register/` | GET/POST | Public | User registration form |
| `/auth/logout/` | GET | Authenticated | User logout |
| `/auth/password-reset/` | GET/POST | Authenticated | Request password reset |
| `/auth/password-reset/done/` | GET | Authenticated | Reset confirmation page |

## 3. Patient URLs

| URL | Method | Access | View Function | Description |
|-----|--------|--------|---------------|-------------|
| `/patient/` | GET | Patient | `patient_dashboard` | Patient dashboard |
| `/patient/appointments/` | GET | Patient | `patient_appointments` | List appointments |
| `/patient/appointments/book/` | GET/POST | Patient | `book_appointment` | Book new appointment |
| `/patient/medical-records/` | GET | Patient | `patient_medical_records` | View medical records |
| `/patient/lab-reports/` | GET | Patient | `patient_lab_reports` | View lab reports |
| `/patient/prescriptions/` | GET | Patient | `patient_prescriptions` | View prescriptions |
| `/patient/prescriptions/<id>/` | GET | Patient | `prescription_detail` | Prescription detail |
| `/patient/medicine-reminders/` | GET | Patient | `medicine_reminders` | View medicine reminders |
| `/patient/medicine-reminders/<id>/taken/` | POST | Patient | `mark_medicine_taken` | Mark dose as taken |
| `/patient/profile/` | GET | Patient | `patient_profile` | View profile |
| `/patient/profile/edit/` | GET/POST | Patient | `edit_profile` | Edit profile |
| `/patient/notifications/` | GET | Patient | `patient_notifications` | View notifications |
| `/patient/account/delete/` | POST | Patient | `delete_account` | Delete account |

## 4. Doctor URLs

| URL | Method | Access | View Function | Description |
|-----|--------|--------|---------------|-------------|
| `/doctor/dashboard/` | GET | Doctor | `doctor_dashboard` | Doctor dashboard |
| `/doctor/patients/` | GET | Doctor | `doctor_patients` | List patients |
| `/doctor/patients/<id>/records/` | GET | Doctor | `patient_records` | Patient records detail |
| `/doctor/schedule/` | GET/POST | Doctor | `doctor_schedule` | Manage schedule |
| `/doctor/appointments/` | GET | Doctor | `doctor_appointments` | List appointments |
| `/doctor/appointments/<id>/approve/` | POST | Doctor | `approve_appointment` | Approve appointment |
| `/doctor/appointments/<id>/reject/` | POST | Doctor | `reject_appointment` | Reject appointment |
| `/doctor/appointments/<id>/complete/` | POST | Doctor | `complete_appointment` | Mark as completed |
| `/doctor/medical-records/` | GET | Doctor | `doctor_medical_records` | List medical records |
| `/doctor/medical-records/add/` | GET/POST | Doctor | `add_medical_record` | Add medical record |
| `/doctor/medical-records/<id>/edit/` | GET/POST | Doctor | `edit_medical_record` | Edit medical record |
| `/doctor/lab-reports/` | GET | Doctor | `doctor_lab_reports` | List lab reports |
| `/doctor/lab-reports/add/` | GET/POST | Doctor | `add_lab_report` | Add lab report |
| `/doctor/prescriptions/` | GET | Doctor | `doctor_prescriptions` | List prescriptions |
| `/doctor/prescriptions/save/` | POST | Doctor | `save_prescription` | Save prescription |
| `/doctor/notifications/` | GET | Doctor | `doctor_notifications` | View notifications |
| `/doctor/notifications/mark-all-read/` | POST | Doctor | `mark_all_read` | Mark all as read |
| `/doctor/profile/` | GET | Doctor | `doctor_profile` | View profile |

## 5. Admin URLs

| URL | Method | Access | View Function | Description |
|-----|--------|--------|---------------|-------------|
| `/admin/` | GET | Admin | `admin_dashboard` | Admin dashboard |
| `/admin/patients/` | GET | Admin | `admin_manage_patients` | Manage patients |
| `/admin/patients/edit/<id>/` | GET/POST | Admin | `edit_patient` | Edit patient |
| `/admin/patients/password/<id>/` | GET/POST | Admin | `change_patient_password` | Reset patient password |
| `/admin/patients/enable/<id>/` | GET | Admin | `enable_patient` | Enable patient account |
| `/admin/patients/disable/<id>/` | GET | Admin | `disable_patient` | Disable patient account |
| `/admin/patients/delete/<id>/` | GET | Admin | `delete_patient` | Delete patient account |
| `/admin/doctor/` | GET | Admin | `admin_manage_doctor` | Manage doctors |
| `/admin/doctor/edit/<id>/` | GET/POST | Admin | `edit_doctor` | Edit doctor |
| `/admin/doctor/password/<id>/` | GET/POST | Admin | `change_doctor_password` | Reset doctor password |
| `/admin/doctor/enable/<id>/` | GET | Admin | `enable_doctor` | Enable doctor account |
| `/admin/doctor/disable/<id>/` | GET | Admin | `disable_doctor` | Disable doctor account |
| `/admin/doctor/delete/<id>/` | GET | Admin | `delete_doctor` | Delete doctor account |
| `/admin/pending-doctors/` | GET | Admin | `pending_doctors` | Pending doctor approvals |
| `/admin/doctors/approve/<id>/` | GET | Admin | `approve_doctor` | Approve doctor |
| `/admin/doctors/reject/<id>/` | GET | Admin | `reject_doctor` | Reject doctor |
| `/admin/appointments/` | GET | Admin | `admin_appointments` | Manage appointments |
| `/admin/accounts/` | GET | Admin | `admin_accounts` | Manage accounts |
| `/admin/accounts/delete/<id>/` | GET | Admin | `delete_account` | Delete account |
| `/admin/reports/` | GET | Admin | `admin_reports` | View reports |

## 6. Role-Based Access Control

| Role | Accessible URL Prefixes |
|------|------------------------|
| Patient | `/patient/`, `/auth/` |
| Doctor | `/doctor/`, `/auth/` |
| Admin | `/admin/`, `/auth/` |
| Public | `/auth/login/`, `/auth/register/` |

### Access Control Implementation

```python
# Example decorators used for access control
from hospital.access import patient_required, doctor_required, admin_required

@patient_required
def patient_dashboard(request):
    ...

@doctor_required
def doctor_dashboard(request):
    ...

@admin_required
def admin_dashboard(request):
    ...
```

## 7. URL Naming Convention

All URLs use Django's `name` parameter for reverse URL resolution:

```python
# Authentication
path('login/', views.login_view, name='login')
path('register/', views.register_view, name='register')
path('logout/', views.logout_view, name='logout')

# Patient
path('', views.patient_dashboard, name='patient_dashboard')
path('appointments/', views.patient_appointments, name='patient_appointments')
path('appointments/book/', views.book_appointment, name='book_appointment')

# Doctor
path('', views.doctor_dashboard, name='doctor_dashboard')
path('patients/', views.doctor_patients, name='doctor_patients')
path('appointments/', views.doctor_appointments, name='doctor_appointments')

# Admin
path('', views.admin_dashboard, name='admin_dashboard')
path('patients/', views.admin_manage_patients, name='admin_manage_patients')
path('doctor/', views.admin_manage_doctor, name='admin_manage_doctor')
```

## 8. URL Resolution Examples

```python
# Template usage
{% url 'patient_roshan:patient_dashboard' %}
{% url 'doctor_siddhartha:doctor_dashboard' %}
{% url 'admin_nishan:admin_dashboard' %}

# Python usage
from django.urls import reverse
reverse('patient_roshan:book_appointment')
reverse('doctor_siddhartha:approve_appointment', args=[appointment_id])
reverse('admin_nishan:edit_patient', args=[patient_id])
```

## 9. Static and Media URLs

| Type | URL Pattern | Configuration |
|------|-------------|---------------|
| Static Files | `/static/` | Django staticfiles |
| Media Files | `/media/` | Cloudinary in production, local in dev |
| Admin Media | `/static/admin/` | Django admin assets |
