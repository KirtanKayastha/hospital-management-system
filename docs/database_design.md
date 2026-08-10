# Database Design

## 1. Database Selection

| Environment | Database | Purpose |
|-------------|----------|---------|
| Development | SQLite | Local development and testing |
| Production | PostgreSQL (Neon) | Live deployment on Render |

## 2. Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      User       │───┐   │  PatientProfile │       │  DoctorProfile  │
│  (Django Auth)  │   │   │                 │       │                 │
├─────────────────┤   │   ├─────────────────┤       ├─────────────────┤
│ id (PK)         │   │   │ id (PK)         │       │ id (PK)         │
│ username        │   └──│ user_id (FK)    │       │ user_id (FK)    │
│ email           │       │ profile_picture │       │ department_id   │
│ first_name      │       │ date_of_birth   │       │ profile_picture │
│ last_name       │       │ gender          │       │ specialization  │
│ user_type       │       │ phone           │       │ qualification   │
│ is_active       │       │ address         │       │ experience      │
│ date_joined     │       │ blood_group     │       │ license_number  │
└─────────────────┘       │ emergency_contact│       │ phone           │
        │                 └─────────────────┘       │ status          │
        │                         │                   └─────────────────┘
        │            ┌─────────────────┐       ┌─────────────────┐
        │            │   Department    │       │ DoctorAvailability│
        │            │                 │       │                   │
        │            ├─────────────────┤       ├─────────────────┤
        │            │ id (PK)         │       │ id (PK)          │
        └───────────│ name            │       │ doctor_id (FK)   │
                     │ slug            │       │ day_of_week      │
                     │ description     │       │ start_time       │
                     │ is_active       │       │ end_time         │
                     └─────────────────┘       │ location         │
                             │                   └─────────────────┘
                             │
┌─────────────────┐   ┌───────────────────────────────────────────┐
│   Appointment   │   │              MedicalRecord                 │
│                 │   │                                           │
├─────────────────┤   ├───────────────────────────────────────────┤
│ id (PK)         │   │ id (PK)                                   │
│ patient_id (FK) │──►│ patient_id (FK)                           │
│ doctor_id (FK)  │──►│ doctor_id (FK)                            │
│ department_id   │   │ appointment_id (FK)                       │
│ appointment_date│   │ department_id                             │
│ appointment_time│   │ diagnosis                                 │
│ reason          │   │ symptoms                                  │
│ status          │   │ treatment                                 │
│ notes           │   │ notes                                     │
│ created_at      │   │ status                                    │
└─────────────────┘   │ visit_date                                │
        │              │ follow_up_date                            │
        │              └───────────────────────────────────────────┘
        │
        ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Prescription  │       │  PrescriptionItem│       │ MedicineReminder│
│                 │       │                   │       │                   │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │──┐   │ id (PK)          │       │ id (PK)          │
│ patient_id (FK) │  │   │ prescription_id  │──┐    │ patient_id (FK)  │
│ doctor_id (FK)  │  │   │ medicine_name    │  │    │ item_id (FK)     │
│ appointment_id  │  └──►│ dosage           │  └──► │ medicine_name    │
│ diagnosis       │      │ frequency        │       │ dosage           │
│ notes           │      │ duration         │       │ remind_at        │
│ prescribed_on   │      │ instructions     │       │ start_date       │
│ is_active       │      └─────────────────┘       │ end_date         │
└─────────────────┘                                │ is_active        │
        │                                          │ last_taken_on    │
        │                                          └─────────────────┘
        ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    LabReport    │       │  BillingInvoice │       │  Notification   │
│                 │       │                   │       │                   │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)          │       │ id (PK)          │
│ patient_id (FK) │       │ invoice_number   │       │ recipient_id(FK) │
│ doctor_id (FK)  │       │ patient_id (FK)  │       │ title            │
│ appointment_id  │       │ appointment_id   │       │ message          │
│ test_name       │       │ amount           │       │ category         │
│ lab_name        │       │ status           │       │ is_read          │
│ ordered_on      │       │ issued_on        │       │ action_url       │
│ result_date     │       │ due_on           │       │ created_at       │
│ status          │       │ paid_on          │       └─────────────────┘
│ report_url      │       │ notes            │
│ summary         │       │ created_at       │
└─────────────────┘       └─────────────────┘
```

## 3. Model Details

### 3.1 User (Django Built-in)

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| username | CharField(150) | Unique username |
| email | EmailField | User email address |
| first_name | CharField(150) | First name |
| last_name | CharField(150) | Last name |
| password | CharField(128) | Hashed password |
| is_active | BooleanField | Account status |
| is_staff | BooleanField | Staff status |
| is_superuser | BooleanField | Superuser status |
| date_joined | DateTimeField | Account creation date |

**Relationships:**
- OneToOne with `PatientProfile` (reverse: `patient_profile`)
- OneToOne with `DoctorProfile` (reverse: `doctor_profile`)
- OneToMany with `Appointment` as patient (reverse: `patient_appointments`)
- OneToMany with `Appointment` as doctor (reverse: `doctor_appointments`)
- OneToMany with `MedicalRecord` as patient (reverse: `medical_records`)
- OneToMany with `MedicalRecord` as doctor (reverse: `authored_medical_records`)
- OneToMany with `Prescription` as patient (reverse: `prescriptions`)
- OneToMany with `Prescription` as doctor (reverse: `authored_prescriptions`)
- OneToMany with `LabReport` as patient (reverse: `lab_reports`)
- OneToMany with `LabReport` as doctor (reverse: `ordered_lab_reports`)
- OneToMany with `BillingInvoice` (reverse: `billing_invoices`)
- OneToMany with `Notification` (reverse: `notifications`)
- OneToMany with `MedicineReminder` (reverse: `medicine_reminders`)

### 3.2 PatientProfile

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| user | OneToOneField(User) | Linked user account |
| profile_picture | ImageField | Profile image (Cloudinary) |
| date_of_birth | DateField | Patient birth date |
| gender | CharField | Gender selection |
| phone | CharField | Contact number |
| address | TextField | Residential address |
| blood_group | CharField | Blood group |
| emergency_contact | CharField | Emergency contact number |

### 3.3 DoctorProfile

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| user | OneToOneField(User) | Linked user account |
| department | ForeignKey(Department) | Assigned department |
| profile_picture | ImageField | Profile image (Cloudinary) |
| specialization | CharField | Medical specialization |
| qualification | CharField | Medical qualification |
| experience | CharField | Years of experience |
| license_number | CharField | Medical license number |
| phone | CharField | Contact number |
| is_available | BooleanField | Availability status |
| status | CharField | Pending/Approved/Rejected |

**Relationships:**
- ForeignKey with `Department` (reverse: `doctors`)
- OneToMany with `Appointment` (reverse: `doctor_appointments`)
- OneToMany with `MedicalRecord` (reverse: `authored_medical_records`)
- OneToMany with `Prescription` (reverse: `authored_prescriptions`)
- OneToMany with `LabReport` (reverse: `ordered_lab_reports`)
- OneToMany with `DoctorAvailability` (reverse: `availability_slots`)

### 3.4 Department

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| name | CharField(120) | Department name (unique) |
| slug | SlugField(140) | URL slug (unique) |
| description | TextField | Department description |
| is_active | BooleanField | Department status |

**Relationships:**
- OneToMany with `DoctorProfile` (reverse: `doctors`)
- OneToMany with `Appointment` (reverse: `appointments`)
- OneToMany with `MedicalRecord` (reverse: `medical_records`)

### 3.5 Appointment

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| patient | ForeignKey(User) | Patient user |
| doctor | ForeignKey(User) | Doctor user |
| department | ForeignKey(Department) | Department |
| appointment_date | DateField | Appointment date |
| appointment_time | TimeField | Appointment time |
| reason | TextField | Reason for visit |
| status | CharField | Pending/Confirmed/Completed/Cancelled/No Show |
| notes | TextField | Additional notes |
| created_at | DateTimeField | Creation timestamp |
| updated_at | DateTimeField | Last update timestamp |

**Constraints:**
- Unique together: (doctor, appointment_date, appointment_time)

**Relationships:**
- ForeignKey with `User` as patient (reverse: `patient_appointments`)
- ForeignKey with `User` as doctor (reverse: `doctor_appointments`)
- ForeignKey with `Department` (reverse: `appointments`)
- OneToOne with `MedicalRecord` (reverse: `medical_record`)
- OneToMany with `Prescription` (reverse: `prescriptions`)
- OneToMany with `LabReport` (reverse: `lab_reports`)
- OneToMany with `BillingInvoice` (reverse: `billing_invoices`)

### 3.6 MedicalRecord

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| patient | ForeignKey(User) | Patient user |
| doctor | ForeignKey(User, null=True) | Attending doctor |
| appointment | OneToOneField(Appointment, null=True) | Related appointment |
| department | ForeignKey(Department, null=True) | Department |
| diagnosis | CharField(200) | Diagnosis |
| symptoms | TextField | Reported symptoms |
| treatment | TextField | Treatment provided |
| notes | TextField | Additional notes |
| status | CharField | Stable/Resolved/Monitoring/Critical |
| visit_date | DateField | Date of visit |
| follow_up_date | DateField | Follow-up date (optional) |
| created_at | DateTimeField | Creation timestamp |
| updated_at | DateTimeField | Last update timestamp |

### 3.7 Prescription

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| patient | ForeignKey(User) | Patient user |
| doctor | ForeignKey(User, null=True) | Prescribing doctor |
| appointment | ForeignKey(Appointment, null=True) | Related appointment |
| diagnosis | CharField(200) | Diagnosis |
| notes | TextField | Additional notes |
| prescribed_on | DateField | Date prescribed |
| is_active | BooleanField | Prescription status |
| created_at | DateTimeField | Creation timestamp |
| updated_at | DateTimeField | Last update timestamp |

**Relationships:**
- ForeignKey with `User` as patient (reverse: `prescriptions`)
- ForeignKey with `User` as doctor (reverse: `authored_prescriptions`)
- ForeignKey with `Appointment` (reverse: `prescriptions`)
- OneToMany with `PrescriptionItem` (reverse: `items`)

### 3.8 PrescriptionItem

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| prescription | ForeignKey(Prescription) | Parent prescription |
| medicine_name | CharField(150) | Medicine name |
| dosage | CharField(100) | Dosage instruction |
| frequency | CharField(100) | Frequency (e.g., "3 times daily") |
| duration | CharField(100) | Duration (e.g., "7 days") |
| instructions | TextField | Additional instructions |

**Relationships:**
- ForeignKey with `Prescription` (reverse: `items`)
- OneToMany with `MedicineReminder` (reverse: `reminders`)

### 3.9 MedicineReminder

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| patient | ForeignKey(User) | Patient user |
| item | ForeignKey(PrescriptionItem) | Source prescription item |
| medicine_name | CharField(150) | Copied medicine name |
| dosage | CharField(100, blank=True) | Copied dosage |
| remind_at | TimeField | Reminder time slot |
| start_date | DateField | Reminder start date |
| end_date | DateField(null=True) | Reminder end date |
| is_active | BooleanField | Reminder status |
| last_taken_on | DateField(null=True) | Last taken date |
| created_at | DateTimeField | Creation timestamp |

**Relationships:**
- ForeignKey with `User` as patient (reverse: `medicine_reminders`)
- ForeignKey with `PrescriptionItem` (reverse: `reminders`)

### 3.10 LabReport

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| patient | ForeignKey(User) | Patient user |
| doctor | ForeignKey(User, null=True) | Ordering doctor |
| appointment | ForeignKey(Appointment, null=True) | Related appointment |
| test_name | CharField(160) | Name of test |
| lab_name | CharField(160) | Laboratory name |
| ordered_on | DateField | Date ordered |
| result_date | DateField(null=True) | Date results available |
| status | CharField | Pending/Ready/In Review |
| report_url | URLField(blank=True) | Link to report file |
| summary | TextField | Result summary |
| created_at | DateTimeField | Creation timestamp |

### 3.11 BillingInvoice

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| invoice_number | CharField(30) | Unique invoice ID |
| patient | ForeignKey(User) | Patient user |
| appointment | ForeignKey(Appointment, null=True) | Related appointment |
| amount | DecimalField(10,2) | Invoice amount |
| status | CharField | Draft/Unpaid/Paid/Void |
| issued_on | DateField | Issue date |
| due_on | DateField(null=True) | Due date |
| paid_on | DateField(null=True) | Payment date |
| notes | TextField | Additional notes |
| created_at | DateTimeField | Creation timestamp |

### 3.12 Notification

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| recipient | ForeignKey(User) | Notification recipient |
| title | CharField(200) | Notification title |
| message | TextField | Notification message |
| category | CharField | General/Appointment/Lab/Billing |
| is_read | BooleanField | Read status |
| action_url | CharField(255, blank=True) | Action link |
| created_at | DateTimeField | Creation timestamp |

### 3.13 DoctorAvailability

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| doctor | ForeignKey(User) | Doctor user |
| day_of_week | PositiveSmallIntegerField | 0=Monday, 6=Sunday |
| start_time | TimeField | Slot start time |
| end_time | TimeField | Slot end time |
| is_active | BooleanField | Slot status |
| location | CharField(120, blank=True) | Clinic location |

## 4. Model Relationships Summary

| Relationship Type | Count | Examples |
|-------------------|-------|----------|
| OneToOne | 3 | User-PatientProfile, User-DoctorProfile, Appointment-MedicalRecord |
| ForeignKey | 18 | Appointment-patient, Prescription-patient, LabReport-doctor |
| OneToMany (reverse FK) | 30+ | User-appointments, Prescription-items |
| ManyToMany | 0 | N/A (no explicit M2M fields) |

## 5. Database Constraints

| Constraint | Model | Fields |
|------------|-------|--------|
| Unique | User | username, email |
| Unique | Department | name, slug |
| Unique | BillingInvoice | invoice_number |
| Unique Together | Appointment | (doctor, appointment_date, appointment_time) |
| Not Null | PatientProfile | user |
| Not Null | DoctorProfile | user, department |
| Cascade Delete | PrescriptionItem | prescription |
| Set Null | MedicalRecord | doctor, appointment, department |
