# System Architecture

## 1. High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph Client["Client Layer"]
        Browser["Web Browser"]
    end

    subgraph Presentation["Presentation Layer"]
        Templates["Django Templates"]
        Static["Static Files (CSS/JS)"]
        Tailwind["Tailwind CSS"]
        Bootstrap["Bootstrap 5"]
    end

    subgraph Application["Application Layer"]
        URLConf["URL Configuration"]
        Views["View Functions"]
        Forms["Django Forms"]
        Middleware["Authentication Middleware"]
    end

    subgraph Business["Business Logic Layer"]
        AuthModule["Auth Module (auth_kirtan)"]
        PatientModule["Patient Module (patient_roshan)"]
        DoctorModule["Doctor Module (doctor_siddhartha)"]
        AdminModule["Admin Module (admin_nishan)"]
        Notifications["Notification System"]
        Reminders["Medicine Reminder Engine"]
    end

    subgraph Data["Data Layer"]
        ORM["Django ORM"]
        Models["Database Models"]
        SQLite["SQLite (Dev)"]
        PostgreSQL["PostgreSQL/Neon (Prod)"]
        Cloudinary["Cloudinary Storage"]
    end

    Browser --> Templates
    Templates --> Views
    Static --> Templates
    Tailwind --> Templates
    Bootstrap --> Templates

    Views --> URLConf
    Views --> Middleware
    Views --> Forms
    Views --> Business

    Business --> ORM
    ORM --> Models
    Models --> SQLite
    Models --> PostgreSQL
    Cloudinary --> Media["Media Files"]
```

## 2. Application Layer Structure

```
hospital_management/
├── hospital/                    # Project Configuration
│   ├── settings.py              # Django settings
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI configuration
│   └── asgi.py                  # ASGI configuration
│
├── auth_kirtan/                 # Authentication Module
│   ├── views.py                 # Login, Register, Password Reset
│   ├── urls.py                  # Auth URLs
│   └── models.py                # Custom user extensions
│
├── patient_roshan/              # Patient Module
│   ├── views.py                 # Patient views
│   ├── urls.py                  # Patient URLs
│   └── models.py                # Patient profile models
│
├── doctor_siddhartha/           # Doctor Module
│   ├── views.py                 # Doctor views
│   ├── urls.py                  # Doctor URLs
│   └── models.py                # Doctor profile models
│
├── admin_nishan/                # Admin Module
│   ├── views.py                 # Admin views
│   ├── urls.py                  # Admin URLs
│   ├── forms.py                 # Admin forms
│   └── models.py                # Core domain models
│
└── templates/                   # Shared templates
    └── base.html                # Base template
```

## 3. Frontend-Backend Interaction Flow

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant D as Django Server
    participant V as View Function
    participant M as Model
    participant DB as Database

    U->>B: Request Page
    B->>D: HTTP Request
    D->>D: URL Routing
    D->>D: Authentication Check
    D->>V: Dispatch to View
    V->>M: Query/Update Data
    M->>DB: SQL Query
    DB->>M: Return Data
    M->>V: Model Instances
    V->>B: Render Template with Context
    B->>U: Display Page
```

## 4. Database Schema (ER Diagram)

```mermaid
erDiagram
    User ||--o| PatientProfile : "has"
    User ||--o| DoctorProfile : "has"
    User ||--o{ Appointment : "books"
    User ||--o{ MedicalRecord : "undergoes"
    User ||--o{ Prescription : "receives"
    User ||--o{ LabReport : "has"
    User ||--o{ BillingInvoice : "pays"
    User ||--o{ Notification : "receives"
    User ||--o{ MedicineReminder : "has"

    DoctorProfile ||--o{ Appointment : "conducts"
    DoctorProfile ||--o{ MedicalRecord : "authors"
    DoctorProfile ||--o{ Prescription : "writes"
    DoctorProfile ||--o{ LabReport : "orders"
    DoctorProfile ||--o{ DoctorAvailability : "has"

    Department ||--o{ DoctorProfile : "employs"
    Department ||--o{ Appointment : "hosts"
    Department ||--o{ MedicalRecord : "belongs_to"

    Appointment ||--o| MedicalRecord : "generates"
    Appointment ||--o| Prescription : "results_in"
    Appointment ||--o{ LabReport : "requires"
    Appointment ||--o{ BillingInvoice : "generates"

    Prescription ||--o{ PrescriptionItem : "contains"
    PrescriptionItem ||--o{ MedicineReminder : "generates"

    User {
        int id PK
        string username
        string email
        string first_name
        string last_name
        string user_type
        boolean is_active
        datetime date_joined
    }

    PatientProfile {
        int id PK
        int user_id FK
        string profile_picture
        date date_of_birth
        string gender
        string phone
        string address
        string blood_group
        string emergency_contact
    }

    DoctorProfile {
        int id PK
        int user_id FK
        int department_id FK
        string profile_picture
        string specialization
        string qualification
        string experience
        string license_number
        string phone
        boolean is_available
        string status
    }

    Appointment {
        int id PK
        int patient_id FK
        int doctor_id FK
        int department_id FK
        date appointment_date
        time appointment_time
        string reason
        string status
        text notes
        datetime created_at
    }

    MedicalRecord {
        int id PK
        int patient_id FK
        int doctor_id FK
        int appointment_id FK
        int department_id FK
        string diagnosis
        text symptoms
        text treatment
        text notes
        string status
        date visit_date
        date follow_up_date
    }

    Prescription {
        int id PK
        int patient_id FK
        int doctor_id FK
        int appointment_id FK
        string diagnosis
        text notes
        date prescribed_on
        boolean is_active
    }

    PrescriptionItem {
        int id PK
        int prescription_id FK
        string medicine_name
        string dosage
        string frequency
        string duration
        text instructions
    }

    MedicineReminder {
        int id PK
        int patient_id FK
        int item_id FK
        string medicine_name
        string dosage
        time remind_at
        date start_date
        date end_date
        boolean is_active
        date last_taken_on
    }

    LabReport {
        int id PK
        int patient_id FK
        int doctor_id FK
        int appointment_id FK
        string test_name
        string lab_name
        date ordered_on
        date result_date
        string status
        url report_url
        text summary
    }

    BillingInvoice {
        int id PK
        string invoice_number
        int patient_id FK
        int appointment_id FK
        decimal amount
        string status
        date issued_on
        date due_on
        date paid_on
    }

    Notification {
        int id PK
        int recipient_id FK
        string title
        text message
        string category
        boolean is_read
        string action_url
        datetime created_at
    }

    Department {
        int id PK
        string name
        string slug
        text description
        boolean is_active
    }

    DoctorAvailability {
        int id PK
        int doctor_id FK
        int day_of_week
        time start_time
        time end_time
        boolean is_active
        string location
    }
```

## 5. URL Routing Structure

```
hospital/
├── urls.py                     # Root URL configuration
│   ├── admin/                  # Django Admin
│   ├── auth/                   # Authentication URLs
│   │   ├── login/
│   │   ├── register/
│   │   ├── logout/
│   │   └── password-reset/
│   ├── patient/                # Patient URLs
│   │   ├── dashboard/
│   │   ├── appointments/
│   │   ├── medical-records/
│   │   ├── lab-reports/
│   │   ├── prescriptions/
│   │   ├── profile/
│   │   ├── notifications/
│   │   └── medicine-reminders/
│   ├── doctor/                 # Doctor URLs
│   │   ├── dashboard/
│   │   ├── patients/
│   │   ├── schedule/
│   │   ├── appointments/
│   │   ├── medical-records/
│   │   ├── lab-reports/
│   │   ├── prescriptions/
│   │   ├── notifications/
│   │   └── profile/
│   └── admin/                  # Admin URLs
│       ├── dashboard/
│       ├── patients/
│       ├── doctors/
│       ├── appointments/
│       ├── accounts/
│       ├── reports/
│       └── pending-doctors/
```

## 6. Authentication Flow

```mermaid
flowchart LR
    A[User Visits Site] --> B{Authenticated?}
    B -->|No| C[Show Login Page]
    C --> D[Submit Credentials]
    D --> E{Valid?}
    E -->|No| F[Show Error]
    F --> C
    E -->|Yes| G{User Type?}
    B -->|Yes| H{User Type?}

    G -->|Patient| I[Patient Dashboard]
    G -->|Doctor| J[Doctor Dashboard]
    G -->|Admin| K[Admin Dashboard]

    H -->|Patient| I
    H -->|Doctor| J
    H -->|Admin| K

    I --> L[Patient Features]
    J --> M[Doctor Features]
    K --> N[Admin Features]
```

## 7. Design Patterns Used

| Pattern | Usage |
|---------|-------|
| MVT (Model-View-Template) | Django's primary architectural pattern |
| Role-Based Access Control | Custom decorators for patient/doctor/admin routes |
| Template Inheritance | Base templates extended by module-specific templates |
| Context Processors | Global notification count injection |
| Signal-Based Automation | Prescription save triggers MedicineReminder creation |
| Repository Pattern (Implicit) | ORM queries encapsulated in view functions |
