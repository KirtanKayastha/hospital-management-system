# User Manual

## 1. Introduction

Welcome to the Hospital Management System (HMS). This manual provides step-by-step instructions for using the system as a Patient, Doctor, or Administrator.

## 2. Getting Started

### 2.1 Accessing the System
1. Open your web browser
2. Navigate to the system URL (e.g., `https://hospital-management.onrender.com`)
3. You will see the login page

### 2.2 Logging In
1. Enter your username and password
2. Click "Login"
3. You will be redirected to your role-specific dashboard

### 2.3 First Time Users
- New patients must register first
- New doctors must be approved by admin before login
- Contact administrator for account issues

---

## 3. Patient Guide

### 3.1 Dashboard

**Purpose:** Overview of your health status and upcoming appointments

**Steps:**
1. After login, you land on the Patient Dashboard
2. View upcoming appointments
3. See recent medical records
4. Check notifications (bell icon)

### 3.2 Booking an Appointment

**Purpose:** Schedule a visit with a doctor

**Steps:**
1. Click "Book Appointment" or navigate to Appointments
2. Select a Department
3. Choose a Doctor
4. Select a Date
5. Available time slots will appear
6. Select a time slot
7. Enter reason for visit
8. Click "Book Appointment"
9. You will receive a notification when the doctor responds

### 3.3 Viewing Appointments

**Purpose:** Check your appointment history

**Steps:**
1. Navigate to "Appointments" from sidebar
2. View all appointments with status (Pending, Confirmed, Completed, Cancelled)
3. Use filters to view specific statuses

### 3.4 Viewing Medical Records

**Purpose:** Access your medical history

**Steps:**
1. Navigate to "Medical Records" from sidebar
2. View all records with diagnosis, treatment, and doctor information
3. Click on any record to view details

### 3.5 Viewing Lab Reports

**Purpose:** Check your laboratory test results

**Steps:**
1. Navigate to "Lab Reports" from sidebar
2. View all lab reports with status (Pending, Ready, In Review)
3. Click "Download" to view the report file

### 3.6 Viewing Prescriptions

**Purpose:** Check your prescriptions and medications

**Steps:**
1. Navigate to "Prescriptions" from sidebar
2. View all prescriptions with medicine details
3. Click on any prescription to see full details including dosage and instructions

### 3.7 Medicine Reminders

**Purpose:** Track your daily medications

**Steps:**
1. Navigate to "Medicine Reminders" from sidebar
2. View all active reminders for today
3. Each reminder shows medicine name, dosage, and time
4. Click "Mark as Taken" after taking your medicine
5. The badge updates showing "X of Y taken today"

### 3.8 Managing Notifications

**Purpose:** Stay updated with system notifications

**Steps:**
1. Click the bell icon in the top navbar
2. View unread notification count
3. Click the bell to go to Notifications page
4. View all notifications (read and unread)
5. Click "Mark all as read" to clear notifications

### 3.9 Editing Profile

**Purpose:** Update your personal information

**Steps:**
1. Navigate to "Profile" from sidebar
2. Click "Edit Profile"
3. Update your information:
   - Profile picture (click to upload)
   - Date of birth
   - Gender
   - Phone number
   - Address
   - Blood group
   - Emergency contact
4. Click "Save Changes"

### 3.10 Deleting Account

**Purpose:** Permanently remove your account

**Steps:**
1. Navigate to "Profile" → "Account Settings"
2. Click "Delete Account"
3. Confirm deletion
4. Your account and all associated data will be permanently removed

---

## 4. Doctor Guide

### 4.1 Dashboard

**Purpose:** Overview of your daily schedule and patient statistics

**Steps:**
1. After login, you land on the Doctor Dashboard
2. View today's appointments
3. See patient statistics
4. Check notifications

### 4.2 Managing Patients

**Purpose:** View patients who have appointments with you

**Steps:**
1. Navigate to "Patients" from sidebar
2. View list of patients
3. Click on a patient to view their records
4. View their medical history, prescriptions, and lab reports

### 4.3 Managing Schedule

**Purpose:** Set your weekly availability

**Steps:**
1. Navigate to "Schedule" from sidebar
2. Select a day of the week
3. Set start and end times
4. Add location (optional)
5. Click "Add Slot"
6. Your availability is now visible to patients

### 4.4 Managing Appointments

**Purpose:** Review and respond to appointment requests

**Steps:**
1. Navigate to "Appointments" from sidebar
2. View all appointments (Pending, Confirmed, Completed, Cancelled)
3. For pending appointments:
   - Click "Approve" to confirm
   - Click "Reject" to decline
4. For confirmed appointments:
   - Click "Complete" after the visit

### 4.5 Adding Medical Records

**Purpose:** Document patient visits

**Steps:**
1. Navigate to "Medical Records" → "Add Record"
2. Select patient
3. Enter diagnosis
4. Enter symptoms
5. Enter treatment provided
6. Add notes (optional)
7. Set status (Stable, Monitoring, Critical, Resolved)
8. Set follow-up date (optional)
9. Click "Save Record"
10. Patient receives notification

### 4.6 Editing Medical Records

**Purpose:** Update existing records

**Steps:**
1. Navigate to "Medical Records"
2. Find the record to edit
3. Click "Edit"
4. Update fields as needed
5. Click "Update Record"

### 4.7 Adding Lab Reports

**Purpose:** Order or add lab reports for patients

**Steps:**
1. Navigate to "Lab Reports" → "Add Report"
2. Select patient
3. Enter test name
4. Enter lab name
5. Set ordered date
6. Upload report URL
7. Add summary
8. Click "Save Report"

### 4.8 Creating Prescriptions

**Purpose:** Prescribe medications to patients

**Steps:**
1. Navigate to "Prescriptions"
2. Select a patient
3. Enter diagnosis
4. Add medicines:
   - Medicine name
   - Dosage
   - Frequency (e.g., "3 times daily", "1-0-1")
   - Duration (e.g., "7 days", "2 weeks")
   - Instructions (optional)
5. Click "Add Medicine" for additional medicines
6. Click "Save Prescription"
7. Medicine reminders are automatically generated for the patient
8. Patient receives notification

### 4.9 Managing Notifications

**Purpose:** Stay updated with system alerts

**Steps:**
1. Click the bell icon in the top navbar
2. View unread notification count
3. Click the bell to go to Notifications page
4. View all notifications
5. Click "Mark all as read" to clear

### 4.10 Editing Profile

**Purpose:** Update your professional information

**Steps:**
1. Navigate to "Profile" from sidebar
2. Click "Edit Profile"
3. Update your information:
   - Profile picture
   - Specialization
   - Qualification
   - Experience
   - Phone number
4. Click "Save Changes"

---

## 5. Admin Guide

### 5.1 Dashboard

**Purpose:** System overview and statistics

**Steps:**
1. After login, you land on the Admin Dashboard
2. View key statistics:
   - Total patients
   - Total doctors
   - Today's appointments
   - Revenue
3. View weekly appointment chart
4. View recent activity

### 5.2 Managing Patients

**Purpose:** Oversee all patient accounts

**Steps:**
1. Navigate to "Patients" from sidebar
2. View all patients with profiles
3. Click "Edit" to modify patient information
4. Click "Change Password" to reset password
5. Click "Enable/Disable" to control login access
6. Click "Delete" to remove patient account

### 5.3 Managing Doctors

**Purpose:** Oversee all doctor accounts

**Steps:**
1. Navigate to "Doctors" from sidebar
2. View all doctors with profiles
3. Click "Edit" to modify doctor information
4. Click "Change Password" to reset password
5. Click "Enable/Disable" to control login access
6. Click "Delete" to remove doctor account

### 5.4 Approving Doctors

**Purpose:** Review and approve new doctor registrations

**Steps:**
1. Navigate to "Pending Doctors" from sidebar
2. View list of doctors awaiting approval
3. Review doctor's information
4. Click "Approve" to grant access
5. Click "Reject" to deny access

### 5.5 Managing Appointments

**Purpose:** Oversee all system appointments

**Steps:**
1. Navigate to "Appointments" from sidebar
2. View all appointments across all patients and doctors
3. Filter by status, date, or doctor
4. View appointment details

### 5.6 Managing Accounts

**Purpose:** View and manage all user accounts

**Steps:**
1. Navigate to "Accounts" from sidebar
2. View all user accounts (patients and doctors)
3. See account status (active/inactive)
4. Delete accounts if necessary

### 5.7 Viewing Reports

**Purpose:** Analyze system data and trends

**Steps:**
1. Navigate to "Reports" from sidebar
2. View appointment trends (weekly chart)
3. View department distribution
4. View total statistics:
   - Total patients
   - Total doctors
   - Total appointments
   - Total records
   - Total prescriptions
   - Total revenue

---

## 6. Notifications Guide

### 6.1 Notification Types

| Type | Trigger | Recipient |
|------|---------|-----------|
| Appointment Approved | Doctor approves appointment | Patient |
| Appointment Rejected | Doctor rejects appointment | Patient |
| Appointment Completed | Doctor marks appointment complete | Patient |
| New Prescription | Doctor creates prescription | Patient |
| Prescription Updated | Doctor updates prescription | Patient |
| Prescription Deleted | Doctor deletes prescription | Patient |
| Medical Record Added | Doctor adds medical record | Patient |
| Medical Record Updated | Doctor edits medical record | Patient |

### 6.2 Reading Notifications

1. Click the bell icon in the top navbar
2. The number shows unread notifications
3. Click the bell to view all notifications
4. Notifications are ordered by newest first
5. Click "Mark all as read" to clear unread count

---

## 7. Troubleshooting

### 7.1 Login Issues
- **Problem:** Cannot login
- **Solution:** Check username and password. Use "Forgot Password" if needed.

### 7.2 Profile Picture Not Uploading
- **Problem:** Profile picture upload fails
- **Solution:** Ensure image is under 5MB and in JPG/PNG format

### 7.3 Not Receiving Emails
- **Problem:** Password reset email not received
- **Solution:** Check spam folder. Contact admin if issue persists.

### 7.4 Appointment Not Showing
- **Problem:** Booked appointment not visible
- **Solution:** Refresh the page. Check if appointment was cancelled by doctor.

### 7.5 Medicine Reminders Not Appearing
- **Problem:** No reminders showing
- **Solution:** Ensure you have active prescriptions. Check with your doctor.

---

## 8. Screenshots

> **Note:** Screenshots should be inserted here for each major page

### 8.1 Login Page
![Login Page](images/login.png)

### 8.2 Patient Dashboard
![Patient Dashboard](images/patient_dashboard.png)

### 8.3 Doctor Dashboard
![Doctor Dashboard](images/doctor_dashboard.png)

### 8.4 Admin Dashboard
![Admin Dashboard](images/admin_dashboard.png)

### 8.5 Appointment Booking
![Appointment Booking](images/book_appointment.png)

### 8.6 Prescription View
![Prescription](images/prescription.png)

### 8.7 Medicine Reminders
![Medicine Reminders](images/medicine_reminders.png)

---

## 9. Support

For technical support or account issues, contact your system administrator.

**System Administrator:** [Admin Name]
**Email:** admin@hospital.com
**Phone:** [Contact Number]

---

*User Manual Version: 1.0*
*Last Updated: August 2026*
