# Module-Wise Documentation

## 1. Authentication Module (auth_kirtan)

### 1.1 Features
- User registration with role selection (Patient/Doctor/Admin)
- Secure login and logout
- Password reset via email (Mailgun integration)
- Role-based redirect after login
- Protected routes with authentication decorators

### 1.2 URLs

| URL Pattern | View Function | Access |
|-------------|---------------|--------|
| `/auth/login/` | `login_view` | Public |
| `/auth/register/` | `register_view` | Public |
| `/auth/logout/` | `logout_view` | Authenticated |
| `/auth/password-reset/` | `password_reset_view` | Authenticated |
| `/auth/password-reset/done/` | `password_reset_done` | Authenticated |

### 1.3 Models

| Model | Fields | Description |
|-------|--------|-------------|
| `User` (Extended) | username, email, first_name, last_name, user_type, is_active | Django's built-in User model with custom extension |

### 1.4 Views

| View | Purpose |
|------|---------|
| `login_view` | Authenticates user and redirects based on role |
| `register_view` | Creates new user account with selected role |
| `logout_view` | Logs out user and redirects to login |
| `password_reset_view` | Sends password reset email via Mailgun |
| `password_reset_done` | Confirmation page after reset request |

---

## 2. Patient Module (patient_roshan)

### 2.1 Features
- Personal dashboard with appointment overview
- Appointment booking with doctor selection and time slots
- Appointment history with status tracking
- Medical records viewing
- Lab reports viewing
- Prescription history
- Medicine reminders with "mark as taken" functionality
- Profile management (view/edit)
- Account deletion
- Real-time notifications

### 2.2 URLs

| URL Pattern | View Function | Access |
|-------------|---------------|--------|
| `/patient/` | `patient_dashboard` | Patient |
| `/patient/appointments/` | `patient_appointments` | Patient |
| `/patient/appointments/book/` | `book_appointment` | Patient |
| `/patient/medical-records/` | `patient_medical_records` | Patient |
| `/patient/lab-reports/` | `patient_lab_reports` | Patient |
| `/patient/prescriptions/` | `patient_prescriptions` | Patient |
| `/patient/prescriptions/<id>/` | `prescription_detail` | Patient |
| `/patient/medicine-reminders/` | `medicine_reminders` | Patient |
| `/patient/medicine-reminders/<id>/taken/` | `mark_medicine_taken` | Patient |
| `/patient/profile/` | `patient_profile` | Patient |
| `/patient/profile/edit/` | `edit_profile` | Patient |
| `/patient/notifications/` | `patient_notifications` | Patient |
| `/patient/account/delete/` | `delete_account` | Patient |

### 2.3 Models

| Model | Key Fields | Description |
|-------|-----------|-------------|
| `PatientProfile` | user (OneToOne), profile_picture, date_of_birth, gender, phone, address, blood_group, emergency_contact | Extended patient information |

### 2.4 Views

| View | Purpose |
|------|---------|
| `patient_dashboard` | Shows upcoming appointments, recent records, notifications |
| `patient_appointments` | Lists all patient appointments with filtering |
| `book_appointment` | Form to book new appointment with doctor selection |
| `patient_medical_records` | Displays patient's medical history |
| `patient_lab_reports` | Shows lab reports with download links |
| `patient_prescriptions` | Lists all prescriptions with medicine details |
| `prescription_detail` | Detailed view of a single prescription |
| `medicine_reminders` | Lists active medicine reminders for the day |
| `mark_medicine_taken` | Marks a reminder dose as taken |
| `patient_profile` | Displays patient profile information |
| `edit_profile` | Allows editing profile details and profile picture |
| `patient_notifications` | Shows all patient notifications with read/unread status |
| `delete_account` | Deletes patient account and associated data |

---

## 3. Doctor Module (doctor_siddhartha)

### 3.1 Features
- Personal dashboard with today's appointments
- Patient list with search
- Schedule management (day-wise availability)
- Appointment approval/rejection/completion
- Medical record creation and editing
- Lab report management
- Prescription creation with multiple medicines
- Automatic medicine reminder generation from prescriptions
- Patient medical records viewing
- Notifications for appointment actions and record updates
- Profile management with profile picture

### 3.2 URLs

| URL Pattern | View Function | Access |
|-------------|---------------|--------|
| `/doctor/dashboard/` | `doctor_dashboard` | Doctor |
| `/doctor/patients/` | `doctor_patients` | Doctor |
| `/doctor/patients/<id>/records/` | `patient_records` | Doctor |
| `/doctor/schedule/` | `doctor_schedule` | Doctor |
| `/doctor/appointments/` | `doctor_appointments` | Doctor |
| `/doctor/appointments/<id>/approve/` | `approve_appointment` | Doctor |
| `/doctor/appointments/<id>/reject/` | `reject_appointment` | Doctor |
| `/doctor/appointments/<id>/complete/` | `complete_appointment` | Doctor |
| `/doctor/medical-records/` | `doctor_medical_records` | Doctor |
| `/doctor/medical-records/add/` | `add_medical_record` | Doctor |
| `/doctor/medical-records/<id>/edit/` | `edit_medical_record` | Doctor |
| `/doctor/lab-reports/` | `doctor_lab_reports` | Doctor |
| `/doctor/lab-reports/add/` | `add_lab_report` | Doctor |
| `/doctor/prescriptions/` | `doctor_prescriptions` | Doctor |
| `/doctor/prescriptions/save/` | `save_prescription` | Doctor |
| `/doctor/notifications/` | `doctor_notifications` | Doctor |
| `/doctor/profile/` | `doctor_profile` | Doctor |

### 3.3 Models

| Model | Key Fields | Description |
|-------|-----------|-------------|
| `DoctorProfile` | user (OneToOne), department (FK), profile_picture, specialization, qualification, experience, license_number, phone, is_available, status | Extended doctor information |

### 3.4 Views

| View | Purpose |
|------|---------|
| `doctor_dashboard` | Shows today's appointments, stats, recent patients |
| `doctor_patients` | Lists patients who have appointments with this doctor |
| `patient_records` | Shows a specific patient's medical records and prescriptions |
| `doctor_schedule` | Manages weekly availability slots |
| `doctor_appointments` | Lists and filters appointments for the doctor |
| `approve_appointment` | Approves a pending appointment |
| `reject_appointment` | Rejects a pending appointment |
| `complete_appointment` | Marks appointment as completed |
| `doctor_medical_records` | Lists medical records authored by doctor |
| `add_medical_record` | Creates new medical record for patient |
| `edit_medical_record` | Updates existing medical record |
| `doctor_lab_reports` | Lists lab reports ordered by doctor |
| `add_lab_report` | Creates new lab report |
| `doctor_prescriptions` | Lists prescriptions written by doctor |
| `save_prescription` | Creates/updates prescription with medicines and auto-generates reminders |
| `doctor_notifications` | Shows doctor notifications with read/unread status |
| `doctor_profile` | Displays doctor profile with specialization details |

---

## 4. Admin Module (admin_nishan)

### 4.1 Features
- Comprehensive dashboard with statistics and charts
- Patient management (CRUD operations)
- Doctor management (CRUD operations, enable/disable, password change)
- Appointment oversight and management
- Account management (enable/disable/delete)
- Reports and analytics with charts
- Pending doctor approval workflow
- Revenue tracking

### 4.2 URLs

| URL Pattern | View Function | Access |
|-------------|---------------|--------|
| `/admin/` | `admin_dashboard` | Admin |
| `/admin/patients/` | `admin_manage_patients` | Admin |
| `/admin/patients/edit/<id>/` | `edit_patient` | Admin |
| `/admin/patients/password/<id>/` | `change_patient_password` | Admin |
| `/admin/patients/enable/<id>/` | `enable_patient` | Admin |
| `/admin/patients/disable/<id>/` | `disable_patient` | Admin |
| `/admin/patients/delete/<id>/` | `delete_patient` | Admin |
| `/admin/doctor/` | `admin_manage_doctor` | Admin |
| `/admin/doctor/edit/<id>/` | `edit_doctor` | Admin |
| `/admin/doctor/password/<id>/` | `change_doctor_password` | Admin |
| `/admin/doctor/enable/<id>/` | `enable_doctor` | Admin |
| `/admin/doctor/disable/<id>/` | `disable_doctor` | Admin |
| `/admin/doctor/delete/<id>/` | `delete_doctor` | Admin |
| `/admin/pending-doctors/` | `pending_doctors` | Admin |
| `/admin/doctors/approve/<id>/` | `approve_doctor` | Admin |
| `/admin/doctors/reject/<id>/` | `reject_doctor` | Admin |
| `/admin/appointments/` | `admin_appointments` | Admin |
| `/admin/accounts/` | `admin_accounts` | Admin |
| `/admin/accounts/delete/<id>/` | `delete_account` | Admin |
| `/admin/reports/` | `admin_reports` | Admin |

### 4.3 Models

| Model | Key Fields | Description |
|-------|-----------|-------------|
| `Department` | name, slug, description, is_active | Hospital departments |
| `DoctorAvailability` | doctor (FK), day_of_week, start_time, end_time, is_active, location | Doctor's weekly schedule slots |
| `Appointment` | patient (FK), doctor (FK), department (FK), appointment_date, appointment_time, reason, status, notes | Appointment booking records |
| `MedicalRecord` | patient (FK), doctor (FK), appointment (OneToOne), department (FK), diagnosis, symptoms, treatment, notes, status, visit_date, follow_up_date | Patient medical history |
| `Prescription` | patient (FK), doctor (FK), appointment (FK), diagnosis, notes, prescribed_on, is_active | Prescription header |
| `PrescriptionItem` | prescription (FK), medicine_name, dosage, frequency, duration, instructions | Individual medicine in prescription |
| `LabReport` | patient (FK), doctor (FK), appointment (FK), test_name, lab_name, ordered_on, result_date, status, report_url, summary | Laboratory test reports |
| `BillingInvoice` | invoice_number, patient (FK), appointment (FK), amount, status, issued_on, due_on, paid_on | Billing records |
| `MedicineReminder` | patient (FK), item (FK), medicine_name, dosage, remind_at, start_date, end_date, is_active, last_taken_on | Generated medicine dose reminders |
| `Notification` | recipient (FK), title, message, category, is_read, action_url, created_at | System notifications |

### 4.4 Views

| View | Purpose |
|------|---------|
| `admin_dashboard` | Shows stats, weekly appointment chart, recent activity, revenue |
| `admin_manage_patients` | Lists all patients with CRUD actions |
| `edit_patient` | Form to edit patient profile |
| `change_patient_password` | Admin can reset patient password |
| `enable_patient` | Enables patient login |
| `disable_patient` | Disables patient login |
| `delete_patient` | Deletes patient account |
| `admin_manage_doctor` | Lists all doctors with CRUD actions |
| `edit_doctor` | Form to edit doctor profile |
| `change_doctor_password` | Admin can reset doctor password |
| `enable_doctor` | Enables doctor login |
| `disable_doctor` | Disables doctor login |
| `delete_doctor` | Deletes doctor account |
| `pending_doctors` | Lists doctors pending approval |
| `approve_doctor` | Approves a doctor registration |
| `reject_doctor` | Rejects a doctor registration |
| `admin_appointments` | Lists all appointments with filtering |
| `admin_accounts` | Lists all user accounts |
| `delete_account` | Deletes any user account |
| `admin_reports` | Shows analytics charts and statistics |
