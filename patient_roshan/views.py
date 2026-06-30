from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# TODO: import models once created
# from .models import Appointment, MedicalRecord, LabReport, PatientProfile


@login_required
def dashboard(request):
    """
    Patient dashboard — shows stats, recent appointments, prescriptions.
    """
    # TODO: replace with real querysets
    # upcoming = Appointment.objects.filter(patient=request.user, status='Confirmed').count()
    # recent = Appointment.objects.filter(patient=request.user).order_by('-date')[:4]

    context = {
        'active_page': 'dashboard',
        'upcoming_count': 3,
        'total_visits': 12,
        'records_count': 7,
        'recent_appointments': [],   # TODO: replace with queryset
        'prescriptions': [],          # TODO: replace with queryset
    }
    return render(request, 'patient_roshan/dashboard.html', context)


@login_required
def book_appointment(request):
    """
    Book a new appointment — shows doctor list + calendar + time slots.
    """
    if request.method == 'POST':
        # TODO: save appointment to DB
        # doctor_id = request.POST.get('doctor_id')
        # date = request.POST.get('appointment_date')
        # time = request.POST.get('appointment_time')
        # reason = request.POST.get('reason')
        messages.success(request, 'Appointment booked successfully!')
        return redirect('patient_roshan:my_appointments')

    context = {
        'active_page': 'book',
        'departments': [],    # TODO: Department.objects.all()
        'doctors': [],        # TODO: Doctor.objects.all()
        'time_slots': [],     # TODO: generate available slots
        'calendar_days': [],  # TODO: generate calendar days for current month
        'selected_date': '',
        'selected_time': '',
    }
    return render(request, 'patient_roshan/book_appointment.html', context)


@login_required
def find_doctor(request):
    """
    Browse and search all available doctors by department and availability.
    """
    department = request.GET.get('department', '')
    search = request.GET.get('search', '')
    availability = request.GET.get('availability', '')

    # TODO: filter doctors from DB
    # doctors = Doctor.objects.all()
    # if department:
    #     doctors = doctors.filter(department_id=department)
    # if search:
    #     doctors = doctors.filter(name__icontains=search)

    context = {
        'active_page': 'finddoctor',
        'departments': [],  # TODO: Department.objects.all()
        'doctors': [],      # TODO: filtered queryset
    }
    return render(request, 'patient_roshan/find_doctor.html', context)


@login_required
def my_appointments(request):
    """
    View all appointments with filter by status and search by doctor name.
    """
    from django.core.paginator import Paginator

    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')

    # TODO: filter appointments from DB
    # appointments = Appointment.objects.filter(patient=request.user).order_by('-date')
    # if status_filter:
    #     appointments = appointments.filter(status=status_filter)
    # if search:
    #     appointments = appointments.filter(doctor__name__icontains=search)

    # paginator = Paginator(appointments, 10)
    # page = request.GET.get('page', 1)
    # appointments_page = paginator.get_page(page)

    status_filters = [
        {'label': 'All', 'value': ''},
        {'label': 'Confirmed', 'value': 'Confirmed'},
        {'label': 'Pending', 'value': 'Pending'},
        {'label': 'Completed', 'value': 'Completed'},
        {'label': 'Cancelled', 'value': 'Cancelled'},
    ]

    context = {
        'active_page': 'appointments',
        'appointments': [],           # TODO: replace with paginator page
        'status_filters': status_filters,
        'current_status': status_filter,
    }
    return render(request, 'patient_roshan/my_appointments.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    """
    Cancel a specific appointment by ID.
    """
    # TODO: get and cancel appointment
    # appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    # appointment.status = 'Cancelled'
    # appointment.save()
    messages.success(request, 'Appointment cancelled.')
    return redirect('patient_roshan:my_appointments')


@login_required
def reschedule_appointment(request, appointment_id):
    """
    Reschedule a specific appointment — redirects to booking page with prefilled data.
    """
    # TODO: pass appointment data to booking form
    return redirect('patient_roshan:book_appointment')


@login_required
def appointment_detail(request, appointment_id):
    """
    View details of a single appointment.
    """
    # TODO: fetch appointment
    # appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    context = {
        'active_page': 'appointments',
        'appointment': None,  # TODO: replace
    }
    return render(request, 'patient_roshan/appointment_detail.html', context)


@login_required
def medical_records(request):
    """
    View medical records — supports list and timeline view toggle.
    """
    context = {
        'active_page': 'records',
        'records': [],   # TODO: MedicalRecord.objects.filter(patient=request.user)
        'patient': None, # TODO: PatientProfile.objects.get(user=request.user)
    }
    return render(request, 'patient_roshan/medical_records.html', context)


@login_required
def lab_reports(request):
    """
    View lab reports ordered by doctors.
    """
    context = {
        'active_page': 'labreports',
        'lab_reports': [],  # TODO: LabReport.objects.filter(patient=request.user)
    }
    return render(request, 'patient_roshan/lab_reports.html', context)


@login_required
def profile(request):
    """
    View and update patient profile information.
    """
    if request.method == 'POST':
        # TODO: update user and patient profile
        # user = request.user
        # user.first_name = request.POST.get('full_name', '').split()[0]
        # user.email = request.POST.get('email')
        # user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('patient_roshan:profile')

    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

    context = {
        'active_page': 'profile',
        'patient': None,       # TODO: PatientProfile.objects.get(user=request.user)
        'blood_groups': blood_groups,
    }
    return render(request, 'patient_roshan/profile.html', context)


@login_required
def update_emergency_contact(request):
    """
    Update emergency contact details.
    """
    if request.method == 'POST':
        # TODO: update emergency contact in PatientProfile
        messages.success(request, 'Emergency contact updated.')
    return redirect('patient_roshan:profile')


@login_required
def change_password(request):
    """
    Change patient account password.
    """
    if request.method == 'POST':
        from django.contrib.auth import update_session_auth_hash
        # TODO: validate old password and set new one
        # old_password = request.POST.get('old_password')
        # new_password = request.POST.get('new_password')
        messages.success(request, 'Password updated successfully.')
    return redirect('patient_roshan:profile')
