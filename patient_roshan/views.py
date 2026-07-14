from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout as auth_logout

def patient_logout(request):
    auth_logout(request)
    return redirect('/patient/login/')
def patient_login(request):
    if request.user.is_authenticated:
        return redirect('patient_roshan:dashboard')
    error = None
    if request.method == 'POST':
        from django.contrib.auth import authenticate, login
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('patient_roshan:dashboard')
        else:
            error = 'Invalid username or password.'
    return render(request, 'patient_roshan/login.html', {'error': error})

# Real Nepali doctors from Neuro Hospital, Clinic One, OM Hospital - Kathmandu
DOCTORS = [
    {
        'id': 1,
        'initials': 'BKB',
        'name': 'Dr. Birendra Kumar Bista',
        'specialization': 'Senior Consultant Neurologist',
        'nmc': '1636',
        'hospital': 'Neuro Hospital, Biratnagar',
        'experience': 20,
        'rating': '4.9',
        'review_count': 134,
        'available_days': 'Sun – Fri',
        'available_slots': ['09:00 AM', '10:30 AM', '02:00 PM'],
        'department': 'Neurology',
        'qualification': 'MBBS, MD (Neurology)',
    },
    {
        'id': 2,
        'initials': 'NKK',
        'name': 'Prof. Dr. Navin Kumar Karna',
        'specialization': 'Senior Consultant Orthopedic Surgeon',
        'nmc': '3103',
        'hospital': 'Neuro Hospital, Biratnagar',
        'experience': 25,
        'rating': '4.8',
        'review_count': 98,
        'available_days': 'Sun – Fri',
        'available_slots': ['08:30 AM', '11:00 AM', '03:00 PM'],
        'department': 'Orthopedics',
        'qualification': 'MBBS, MS (Orthopedic Surgery)',
    },
    {
        'id': 3,
        'initials': 'NRS',
        'name': 'Dr. Nikesh Raj Shrestha',
        'specialization': 'Senior Consultant Interventional Cardiologist',
        'nmc': '3195',
        'hospital': 'Neuro Hospital, Biratnagar',
        'experience': 18,
        'rating': '4.9',
        'review_count': 112,
        'available_days': 'Sun – Fri',
        'available_slots': ['09:00 AM', '10:00 AM', '04:00 PM'],
        'department': 'Cardiology',
        'qualification': 'MBBS, MD, DM (Cardiology)',
    },
    {
        'id': 4,
        'initials': 'ST',
        'name': 'Dr. Sanjeev Thapa',
        'specialization': 'Cardiologist',
        'nmc': '',
        'hospital': 'Clinic One, Lalitpur',
        'experience': 15,
        'rating': '4.7',
        'review_count': 87,
        'available_days': 'Mon only (5 PM onwards)',
        'available_slots': ['05:00 PM', '05:30 PM', '06:00 PM'],
        'department': 'Cardiology',
        'qualification': 'MD (Internal Medicine, BPKIHS), DM (Cardiology, IOM, TU)',
    },
    {
        'id': 5,
        'initials': 'RK',
        'name': 'Dr. Roshan Khatiwada',
        'specialization': 'Senior Consultant Neurosurgeon',
        'nmc': '8369',
        'hospital': 'Neuro Hospital, Biratnagar',
        'experience': 16,
        'rating': '4.8',
        'review_count': 76,
        'available_days': 'Sun – Fri',
        'available_slots': ['10:00 AM', '01:00 PM', '03:30 PM'],
        'department': 'Neurology',
        'qualification': 'MBBS, MCh (Neurosurgery)',
    },
]

# Real patient data - Roshan Ansari
PATIENT = {
    'full_name': 'Roshan Ansari',
    'email': 'PatientRoshan@gmail.com',
    'phone': '+977 9800000000',
    'dob': '2004-11-20',
    'age': 20,
    'gender': 'Male',
    'blood_group': 'O+',
    'address': 'Kathmandu, Bagmati Province, Nepal',
    'patient_id': 'HM-2024-089',
    'emergency_contact_name': 'Irfat Ansari',
    'emergency_contact_relation': 'Brother',
    'emergency_contact_phone': '+977 9800000001',
}


@login_required
def dashboard(request):
    recent_appointments = [
        {'date': '12 Jul 2025', 'time': '09:00 AM', 'doctor_initials': 'NRS', 'doctor_name': 'Dr. Nikesh Raj Shrestha', 'department': 'Cardiology', 'status': 'Confirmed'},
        {'date': '18 Jul 2025', 'time': '10:30 AM', 'doctor_initials': 'BKB', 'doctor_name': 'Dr. Birendra Kumar Bista', 'department': 'Neurology', 'status': 'Pending'},
        {'date': '24 Jul 2025', 'time': '08:30 AM', 'doctor_initials': 'NKK', 'doctor_name': 'Prof. Dr. Navin Kumar Karna', 'department': 'Orthopedics', 'status': 'Confirmed'},
        {'date': '02 Aug 2025', 'time': '05:00 PM', 'doctor_initials': 'ST', 'doctor_name': 'Dr. Sanjeev Thapa', 'department': 'Cardiology', 'status': 'Completed'},
    ]
    prescriptions = [
        {'medicine': 'Amlodipine 5mg', 'refill_date': 'Aug 01, 2025'},
        {'medicine': 'Aspirin 75mg', 'refill_date': 'Aug 15, 2025'},
    ]
    context = {
        'active_page': 'dashboard',
        'upcoming_count': 3,
        'total_visits': 12,
        'records_count': 7,
        'recent_appointments': recent_appointments,
        'prescriptions': prescriptions,
        'patient': PATIENT,
    }
    return render(request, 'patient_roshan/dashboard.html', context)


@login_required
def book_appointment(request):
    if request.method == 'POST':
        from .models import Appointment
        Appointment.objects.create(
            patient=request.user,
            doctor_name=request.POST.get('doctor_name', 'Unknown'),
            department=request.POST.get('department', 'Unknown'),
            date=request.POST.get('appointment_date'),
            time=request.POST.get('appointment_time'),
            reason=request.POST.get('reason'),
            status='Pending'
        )
        messages.success(request, 'Appointment booked successfully!')
        return redirect('patient_roshan:my_appointments')

    departments = list({d['department'] for d in DOCTORS})
    time_slots = [
        {'label': '09:00 AM', 'value': '09:00', 'is_booked': False},
        {'label': '09:30 AM', 'value': '09:30', 'is_booked': False},
        {'label': '10:00 AM', 'value': '10:00', 'is_booked': False},
        {'label': '10:30 AM', 'value': '10:30', 'is_booked': False},
        {'label': '11:00 AM', 'value': '11:00', 'is_booked': False},
        {'label': '11:30 AM', 'value': '11:30', 'is_booked': True},
        {'label': '02:00 PM', 'value': '14:00', 'is_booked': False},
        {'label': '03:30 PM', 'value': '15:30', 'is_booked': False},
        {'label': '04:00 PM', 'value': '16:00', 'is_booked': False},
    ]
    calendar_days = [
        {'number': 29, 'date': '', 'is_past': True, 'is_selected': False},
        {'number': 30, 'date': '', 'is_past': True, 'is_selected': False},
        {'number': 1,  'date': '2025-07-01', 'is_past': False, 'is_selected': False},
        {'number': 2,  'date': '2025-07-02', 'is_past': False, 'is_selected': False},
        {'number': 3,  'date': '2025-07-03', 'is_past': False, 'is_selected': False},
        {'number': 4,  'date': '2025-07-04', 'is_past': False, 'is_selected': False},
        {'number': 5,  'date': '2025-07-05', 'is_past': False, 'is_selected': False},
        {'number': 6,  'date': '2025-07-06', 'is_past': False, 'is_selected': False},
        {'number': 7,  'date': '2025-07-07', 'is_past': False, 'is_selected': False},
        {'number': 8,  'date': '2025-07-08', 'is_past': False, 'is_selected': False},
        {'number': 9,  'date': '2025-07-09', 'is_past': False, 'is_selected': False},
        {'number': 10, 'date': '2025-07-10', 'is_past': False, 'is_selected': False},
        {'number': 11, 'date': '2025-07-11', 'is_past': False, 'is_selected': False},
        {'number': 12, 'date': '2025-07-12', 'is_past': False, 'is_selected': True},
        {'number': 13, 'date': '2025-07-13', 'is_past': False, 'is_selected': False},
        {'number': 14, 'date': '2025-07-14', 'is_past': False, 'is_selected': False},
        {'number': 15, 'date': '2025-07-15', 'is_past': False, 'is_selected': False},
    ]
    context = {
        'active_page': 'book',
        'departments': [{'id': i, 'name': d} for i, d in enumerate(departments, 1)],
        'doctors': DOCTORS,
        'time_slots': time_slots,
        'calendar_days': calendar_days,
        'selected_date': '2025-07-12',
        'selected_time': '10:00',
    }
    return render(request, 'patient_roshan/book_appointment.html', context)


@login_required
def find_doctor(request):
    context = {
        'active_page': 'finddoctor',
        'doctors': DOCTORS,
        'departments': list({d['department'] for d in DOCTORS}),
    }
    return render(request, 'patient_roshan/find_doctor.html', context)


@login_required
def my_appointments(request):
    from .models import Appointment
    appointments = Appointment.objects.filter(patient=request.user)
    status_filters = [
        {'label': 'All', 'value': ''},
        {'label': 'Confirmed', 'value': 'Confirmed'},
        {'label': 'Pending', 'value': 'Pending'},
        {'label': 'Completed', 'value': 'Completed'},
        {'label': 'Cancelled', 'value': 'Cancelled'},
    ]
    context = {
        'active_page': 'appointments',
        'appointments': appointments,
        'status_filters': status_filters,
        'current_status': '',
    }
    return render(request, 'patient_roshan/my_appointments.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    messages.success(request, 'Appointment cancelled.')
    return redirect('patient_roshan:my_appointments')


@login_required
def reschedule_appointment(request, appointment_id):
    return redirect('patient_roshan:book_appointment')


@login_required
def appointment_detail(request, appointment_id):
    context = {'active_page': 'appointments'}
    return render(request, 'patient_roshan/my_appointments.html', context)


@login_required
def medical_records(request):
    records = [
        {
            'date': '28 Jun 2025', 'time': '10:30 AM',
            'diagnosis': 'Hypertension', 'color': '#ba1a1a',
            'doctor_name': 'Dr. Nikesh Raj Shrestha',
            'doctor_specialization': 'Interventional Cardiologist',
            'status': 'STABLE', 'department': 'Cardiology',
            'notes': 'BP recorded at 145/95. Adjustment to Amlodipine dosage recommended. Sodium intake to be reduced.',
        },
        {
            'date': '15 Jun 2025', 'time': '02:15 PM',
            'diagnosis': 'Seasonal Allergy', 'color': '#784b00',
            'doctor_name': 'Dr. Birendra Kumar Bista',
            'doctor_specialization': 'Senior Consultant Neurologist',
            'status': 'RESOLVED', 'department': 'Neurology',
            'notes': 'Prescribed antihistamines. Symptoms resolved. Follow-up in 4 weeks.',
        },
        {
            'date': '02 May 2025', 'time': '09:00 AM',
            'diagnosis': 'Routine Checkup', 'color': '#004ac6',
            'doctor_name': 'Prof. Dr. Navin Kumar Karna',
            'doctor_specialization': 'Senior Consultant Orthopedic Surgeon',
            'status': 'CLEAR', 'department': 'Orthopedics',
            'notes': 'All vitals normal. BMI 22.5. No abnormalities detected.',
        },
    ]

    class FakePatient:
        blood_group = 'O+'
        age = 20
        gender = 'Male'

    context = {
        'active_page': 'records',
        'records': records,
        'patient': FakePatient(),
    }
    return render(request, 'patient_roshan/medical_records.html', context)


@login_required
def lab_reports(request):
    reports = [
        {'date': '15 Jun 2025', 'lab_name': 'Norvic Hospital Lab, Kathmandu', 'test_name': 'Complete Blood Count (CBC)', 'ordered_by': 'Dr. Nikesh Raj Shrestha', 'status': 'Ready', 'file_url': '#'},
        {'date': '15 Jun 2025', 'lab_name': 'Norvic Hospital Lab, Kathmandu', 'test_name': 'Lipid Profile', 'ordered_by': 'Dr. Sanjeev Thapa', 'status': 'Ready', 'file_url': '#'},
        {'date': '20 Jul 2025', 'lab_name': 'Clinic One Lab, Lalitpur', 'test_name': 'Blood Sugar (Fasting)', 'ordered_by': 'Dr. Birendra Kumar Bista', 'status': 'Pending', 'file_url': ''},
        {'date': '20 Jul 2025', 'lab_name': 'Clinic One Lab, Lalitpur', 'test_name': 'Thyroid Function Test (TFT)', 'ordered_by': 'Dr. Sanjeev Thapa', 'status': 'Pending', 'file_url': ''},
    ]
    context = {
        'active_page': 'labreports',
        'lab_reports': reports,
    }
    return render(request, 'patient_roshan/lab_reports.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        messages.success(request, 'Profile updated successfully!')
        return redirect('patient_roshan:profile')

    class FakePatient:
        blood_group = 'O+'
        age = 20
        gender = 'Male'
        phone = '+977 9800000000'
        address = 'Kathmandu, Bagmati Province, Nepal'
        emergency_contact_name = 'Irfat Ansari'
        emergency_contact_relation = 'Brother'
        emergency_contact_phone = '+977 9800000001'
        dob = None

    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    context = {
        'active_page': 'profile',
        'patient': FakePatient(),
        'blood_groups': blood_groups,
    }
    return render(request, 'patient_roshan/profile.html', context)


@login_required
def update_emergency_contact(request):
    if request.method == 'POST':
        messages.success(request, 'Emergency contact updated.')
    return redirect('patient_roshan:profile')


@login_required
def change_password(request):
    if request.method == 'POST':
        messages.success(request, 'Password updated successfully.')
    return redirect('patient_roshan:profile')

@login_required
def prescriptions(request):
    prescriptions = [
        {'date': '28 Jun 2025', 'medicine': 'Amlodipine 5mg', 'dosage': '1 tab / day', 'doctor': 'Dr. Nikesh Raj Shrestha', 'status': 'Active'},
        {'date': '28 Jun 2025', 'medicine': 'Aspirin 75mg', 'dosage': '1 tab / day', 'doctor': 'Dr. Sanjeev Thapa', 'status': 'Active'},
        {'date': '15 Jun 2025', 'medicine': 'Paracetamol 500mg', 'dosage': 'As needed', 'doctor': 'Dr. Birendra Kumar Bista', 'status': 'Completed'},
    ]
    context = {
        'active_page': 'prescriptions',
        'prescriptions': prescriptions,
    }
    return render(request, 'patient_roshan/prescriptions.html', context)