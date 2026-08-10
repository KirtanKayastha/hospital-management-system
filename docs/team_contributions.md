# Team Contributions

## 1. Team Overview

| Name | Role | Department | Contribution % |
|------|------|------------|----------------|
| Kirtan | Team Lead | Full Stack | 30% |
| Nishan | Backend Developer | Admin Module | 25% |
| Roshan | Backend Developer | Patient Module | 25% |
| Siddhartha | Backend Developer | Doctor Module | 20% |

## 2. Individual Contributions

### 2.1 Kirtan - Team Lead

| Category | Contribution | Key Deliverables |
|----------|-------------|------------------|
| **Project Setup** | Initial Django project configuration, Git repository setup, development environment | `manage.py`, `settings.py`, `.gitignore` |
| **Authentication Module** | Complete auth system with registration, login, password reset | `auth_kirtan/` app, email integration |
| **Integration** | Connected all modules, ensured consistent data flow | URL routing, middleware, context processors |
| **Deployment** | Render deployment, Neon PostgreSQL setup, Cloudinary configuration | `build.sh`, environment variables, deployment docs |
| **Code Review** | Reviewed all modules for consistency and best practices | Code quality assurance |
| **Documentation** | Project overview, architecture, deployment guide | This documentation set |

**Focus Areas:**
- System architecture and design patterns
- Cross-module integration
- Production deployment pipeline
- Team coordination and sprint planning

**Lines of Code (Approximate):** 2,500+

**Key Files:**
- `hospital/settings.py`
- `hospital/urls.py`
- `auth_kirtan/views.py`
- `hospital/notifications.py`
- `hospital/reminders.py`

---

### 2.2 Nishan - Backend Developer (Admin Module)

| Category | Contribution | Key Deliverables |
|----------|-------------|------------------|
| **Admin Dashboard** | Comprehensive dashboard with statistics and charts | `admin_dashboard` view, analytics |
| **Patient Management** | Full CRUD operations for patients | `admin_manage_patients`, `edit_patient` |
| **Doctor Management** | Full CRUD operations for doctors | `admin_manage_doctor`, `edit_doctor` |
| **Account Management** | Enable/disable/delete accounts | `admin_accounts`, `delete_account` |
| **Pending Approvals** | Doctor approval workflow | `pending_doctors`, `approve_doctor`, `reject_doctor` |
| **Reports & Analytics** | Appointment trends, department distribution, revenue | `admin_reports` view |
| **Core Models** | Database models for all domain entities | `admin_nishan/models.py` |

**Focus Areas:**
- Administrative functionality
- Database model design
- CRUD operations and business logic
- Reporting and analytics

**Lines of Code (Approximate):** 3,000+

**Key Files:**
- `admin_nishan/models.py`
- `admin_nishan/views.py`
- `admin_nishan/forms.py`
- `admin_nishan/urls.py`

---

### 2.3 Roshan - Backend Developer (Patient Module)

| Category | Contribution | Key Deliverables |
|----------|-------------|------------------|
| **Patient Dashboard** | Overview with appointments and records | `patient_dashboard` view |
| **Appointment Booking** | Booking flow with doctor and time selection | `book_appointment` view, AJAX time slots |
| **Medical Records** | Viewing medical history | `patient_medical_records` view |
| **Lab Reports** | Viewing lab reports with download | `patient_lab_reports` view |
| **Prescriptions** | Viewing prescription history | `patient_prescriptions` view |
| **Medicine Reminders** | Daily dose tracking with "mark taken" | `medicine_reminders`, `mark_medicine_taken` |
| **Profile Management** | View/edit profile with picture upload | `patient_profile`, `edit_profile` |
| **Notifications** | Patient notification center | `patient_notifications` view |

**Focus Areas:**
- Patient experience and workflows
- Appointment booking system
- Medicine reminder system
- Profile management

**Lines of Code (Approximate):** 2,800+

**Key Files:**
- `patient_roshan/views.py`
- `patient_roshan/urls.py`
- `patient_roshan/templates/patient_roshan/*.html`

---

### 2.4 Siddhartha - Backend Developer (Doctor Module)

| Category | Contribution | Key Deliverables |
|----------|-------------|------------------|
| **Doctor Dashboard** | Today's appointments and stats | `doctor_dashboard` view |
| **Patient Management** | Patient list with records | `doctor_patients`, `patient_records` |
| **Schedule Management** | Weekly availability management | `doctor_schedule` view |
| **Appointment Actions** | Approve, reject, complete | `approve_appointment`, `reject_appointment`, `complete_appointment` |
| **Medical Records** | Add/edit medical records | `add_medical_record`, `edit_medical_record` |
| **Lab Reports** | Add lab reports | `add_lab_report` view |
| **Prescriptions** | Create prescriptions with medicines | `save_prescription` view |
| **Notifications** | Doctor notification center | `doctor_notifications` view |
| **Profile** | Doctor profile with picture | `doctor_profile` view |

**Focus Areas:**
- Doctor workflows and approval processes
- Prescription management system
- Medical records management
- Notification system for doctors

**Lines of Code (Approximate):** 2,600+

**Key Files:**
- `doctor_siddhartha/views.py`
- `doctor_siddhartha/urls.py`
- `doctor_siddhartha/templates/doc_siddhartha/*.html`

---

## 3. Work Distribution

### 3.1 By Module

| Module | Primary Developer | Contribution % |
|--------|-------------------|----------------|
| Authentication | Kirtan | 100% |
| Admin Module | Nishan | 100% |
| Patient Module | Roshan | 100% |
| Doctor Module | Siddhartha | 100% |
| Shared Components | Kirtan | 100% |

### 3.2 By Task Type

| Task Type | Primary | Contribution % |
|-----------|---------|----------------|
| Backend Logic | All members | Distributed |
| Frontend Templates | All members | Distributed |
| Database Design | Nishan (lead), Kirtan | Collaborative |
| Testing | Kirtan (lead), All members | Collaborative |
| Documentation | Kirtan (lead), All members | Collaborative |
| Deployment | Kirtan | 100% |

## 4. Collaboration Tools

| Tool | Purpose |
|------|---------|
| Git/GitHub | Version control and collaboration |
| VS Code | Development IDE |
| Discord/Slack | Team communication |
| Draw.io | Architecture diagrams |
| Markdown | Documentation |

## 5. Sprint Timeline

| Sprint | Duration | Focus | Deliverables |
|--------|----------|-------|-------------|
| Sprint 1 | Week 1-2 | Project Setup & Auth | Django project, user authentication |
| Sprint 2 | Week 3-4 | Admin Module | Dashboard, CRUD operations |
| Sprint 3 | Week 5-6 | Patient Module | Dashboard, booking, records |
| Sprint 4 | Week 7-8 | Doctor Module | Dashboard, schedule, prescriptions |
| Sprint 5 | Week 9-10 | Integration & Polish | Notifications, reminders, UI polish |
| Sprint 6 | Week 11-12 | Testing & Deployment | Testing, bug fixes, deployment |

## 6. Code Statistics

| Metric | Value |
|--------|-------|
| Total Python Files | 30+ |
| Total Template Files | 40+ |
| Total Migrations | 10+ |
| Total Models | 13 |
| Total Views | 60+ |
| Total URLs | 50+ |
| Lines of Code (Approx) | 12,000+ |

## 7. Git Contribution Summary

| Member | Commits | Files Changed | Additions | Deletions |
|--------|---------|---------------|-----------|-----------|
| Kirtan | 45+ | 80+ | 8,000+ | 2,000+ |
| Nishan | 35+ | 60+ | 6,000+ | 1,500+ |
| Roshan | 30+ | 55+ | 5,500+ | 1,200+ |
| Siddhartha | 28+ | 50+ | 5,000+ | 1,000+ |

## 8. Key Achievements by Team Member

### Kirtan
- Led the team and coordinated development efforts
- Designed the overall system architecture
- Implemented the authentication and notification systems
- Successfully deployed the application to Render
- Created comprehensive documentation

### Nishan
- Designed and implemented the complete admin module
- Created all core database models
- Built the reports and analytics system
- Implemented the doctor approval workflow
- Ensured data integrity across admin operations

### Roshan
- Built the complete patient-facing interface
- Implemented the appointment booking system
- Created the medicine reminder system
- Developed the notification center for patients
- Ensured smooth patient workflows

### Siddhartha
- Developed the doctor dashboard and management tools
- Implemented the prescription system with auto-reminders
- Built the medical records management for doctors
- Created the notification system for doctors
- Ensured doctor-specific workflows are intuitive
