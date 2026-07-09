from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages

from .models import Patient, Appointment, Prescription, DoctorProfile, Availability
from .forms import PrescriptionForm, PrescriptionItemFormSet, AvailabilityForm


def _get_doctor_profile(request):
    return get_object_or_404(DoctorProfile, user=request.user)


@login_required
def dashboard(request):
    doctor = _get_doctor_profile(request)
    today = timezone.now().date()

    todays_appointments = Appointment.objects.filter(doctor=doctor, date=today)
    recent_patients = Patient.objects.filter(assigned_doctor=doctor).order_by('-created_at')[:5]
    pending_prescriptions_count = Prescription.objects.filter(
        doctor=doctor, items__is_active=True
    ).distinct().count()

    context = {
        'doctor': doctor,
        'today': today,
        'todays_appointments': todays_appointments,
        'recent_patients': recent_patients,
        'total_patients': Patient.objects.filter(assigned_doctor=doctor).count(),
        'appointments_count': todays_appointments.count(),
        'completed_count': todays_appointments.filter(status='completed').count(),
        'pending_prescriptions_count': pending_prescriptions_count,
    }
    return render(request, 'doc_siddhartha/doctor_dashboard.html', context)


@login_required
def schedule(request):
    doctor = _get_doctor_profile(request)
    week_start = request.GET.get('week_start')
    if week_start:
        start_date = timezone.datetime.strptime(week_start, '%Y-%m-%d').date()
    else:
        today = timezone.now().date()
        start_date = today - timezone.timedelta(days=today.weekday())
    end_date = start_date + timezone.timedelta(days=6)

    week_appointments = Appointment.objects.filter(
        doctor=doctor, date__range=(start_date, end_date)
    ).select_related('patient')

    availability = Availability.objects.filter(doctor=doctor, is_active=True)

    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            for day in form.cleaned_data['days']:
                Availability.objects.update_or_create(
                    doctor=doctor,
                    day_of_week=day,
                    start_time=form.cleaned_data['start_time'],
                    defaults={
                        'end_time': form.cleaned_data['end_time'],
                        'slot_duration_minutes': form.cleaned_data['slot_duration_minutes'],
                    },
                )
            messages.success(request, 'Availability schedule updated successfully.')
            return redirect('doctor:schedule')
    else:
        form = AvailabilityForm()

    context = {
        'doctor': doctor,
        'start_date': start_date,
        'end_date': end_date,
        'week_appointments': week_appointments,
        'availability': availability,
        'form': form,
    }
    return render(request, 'doc_siddhartha/schedule.html', context)


@login_required
def update_appointment_status(request, appointment_id):
    """Quick status change (pending/confirmed/completed/cancelled) from the Schedule page."""
    doctor = _get_doctor_profile(request)
    appt = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = dict(Appointment.STATUS_CHOICES)
        if new_status in valid_statuses:
            appt.status = new_status
            appt.save()
            messages.success(request, f"{appt.patient.full_name}'s appointment marked as {appt.get_status_display()}.")
    return redirect('doctor:schedule')


@login_required
def patients_list(request):
    doctor = _get_doctor_profile(request)
    query = request.GET.get('q', '')

    patients = Patient.objects.filter(assigned_doctor=doctor)
    if query:
        patients = patients.filter(full_name__icontains=query)

    selected_id = request.GET.get('patient')
    if selected_id:
        selected_patient = get_object_or_404(Patient, id=selected_id, assigned_doctor=doctor)
    else:
        selected_patient = patients.first()

    context = {
        'doctor': doctor,
        'patients': patients,
        'query': query,
        'selected_patient': selected_patient,
    }
    return render(request, 'doc_siddhartha/patients_records.html', context)


@login_required
def prescriptions(request, patient_id=None):
    doctor = _get_doctor_profile(request)
    patient = get_object_or_404(Patient, id=patient_id, assigned_doctor=doctor) if patient_id else None

    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = doctor
            prescription.patient = patient
            prescription.save()
            formset.instance = prescription
            formset.save()
            messages.success(request, 'Prescription saved successfully.')
            return redirect('doctor:prescriptions', patient_id=patient.id)
    else:
        form = PrescriptionForm()
        formset = PrescriptionItemFormSet()

    if patient:
        past_prescriptions = Prescription.objects.filter(patient=patient)
    else:
        past_prescriptions = Prescription.objects.filter(doctor=doctor).select_related('patient').order_by('-date_issued')[:20]

    context = {
        'doctor': doctor,
        'patient': patient,
        'form': form,
        'formset': formset,
        'past_prescriptions': past_prescriptions,
    }
    return render(request, 'doc_siddhartha/prescription.html', context)


@login_required
def prescription_detail(request, prescription_id):
    doctor = _get_doctor_profile(request)
    rx = get_object_or_404(Prescription, id=prescription_id, doctor=doctor)
    context = {'doctor': doctor, 'rx': rx}
    return render(request, 'doc_siddhartha/prescription_detail.html', context)


@login_required
def delete_prescription(request, prescription_id):
    doctor = _get_doctor_profile(request)
    rx = get_object_or_404(Prescription, id=prescription_id, doctor=doctor)
    if request.method == 'POST':
        patient_id = rx.patient_id
        patient_name = rx.patient.full_name
        rx.delete()
        messages.success(request, f"Prescription for {patient_name} deleted.")
        if patient_id:
            return redirect('doctor:prescriptions', patient_id=patient_id)
    return redirect('doctor:prescriptions')