from datetime import date, datetime, timedelta

from django.contrib import messages
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from admin_nishan.models import Appointment, Department, DoctorAvailability, LabReport, MedicalRecord, Notification, Prescription, PrescriptionItem
from hospital.access import doctor_required
from patient_roshan.models import PatientProfile
from .models import DoctorProfile


def _default_department():
    department, _ = Department.objects.get_or_create(
        slug="general-medicine",
        defaults={"name": "General Medicine", "description": "General patient care and triage."},
    )
    return department


def _doctor_profile(user):
    profile, created = DoctorProfile.objects.get_or_create(
        user=user,
        defaults={
            "department": _default_department(),
            "specialization": "General Medicine",
            "qualification": "",
            "experience_years": 0,
            "license_number": "",
            "phone": "",
            "consultation_fee": 0,
            "bio": "",
            "status": DoctorProfile.STATUS_PENDING,
        },
    )
    if created and not profile.specialization:
        profile.specialization = "General Medicine"
        profile.department = _default_department()
        profile.save(update_fields=["specialization", "department"])
    return profile


def _today_schedule(doctor_user):
    today = timezone.localdate()
    appointments = (
        Appointment.objects.filter(doctor=doctor_user, appointment_date=today)
        .select_related("patient", "department")
        .order_by("appointment_time")
    )
    return appointments


def _recent_patients(doctor_user):
    patient_ids = (
        Appointment.objects.filter(doctor=doctor_user)
        .order_by("-appointment_date", "-appointment_time")
        .values_list("patient_id", flat=True)
        .distinct()[:8]
    )
    patients = []
    for patient_id in patient_ids:
        latest = Appointment.objects.filter(doctor=doctor_user, patient_id=patient_id).select_related("patient").order_by("-appointment_date", "-appointment_time").first()
        if latest:
            patients.append(latest)
    return patients


@doctor_required
def doctor_dashboard(request):
    doctor_profile = _doctor_profile(request.user)
    today = timezone.localdate()
    todays_appointments = _today_schedule(request.user)
    pending_prescriptions = Prescription.objects.filter(doctor=request.user, is_active=True).count()
    total_patients = Appointment.objects.filter(doctor=request.user).values("patient_id").distinct().count()

    context = {
        "doctor_profile": doctor_profile,
        "total_patients": total_patients,
        "todays_appointments": todays_appointments.count(),
        "pending_prescriptions": pending_prescriptions,
        "today_schedule": todays_appointments,
        "recent_patients": _recent_patients(request.user),
        "notifications": Notification.objects.filter(recipient=request.user, is_read=False)[:5],
        "today_label": today.strftime("%A, %B %d"),
    }
    return render(request, "doc_siddhartha/doctor_dashboard.html", context)


@doctor_required
def schedule(request):
    doctor_profile = _doctor_profile(request.user)
    if request.method == "POST":
        day_of_week = request.POST.get("day_of_week")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        is_active = request.POST.get("is_active") == "on"
        if day_of_week and start_time and end_time:
            DoctorAvailability.objects.create(
                doctor=request.user,
                day_of_week=int(day_of_week),
                start_time=datetime.strptime(start_time, "%H:%M").time(),
                end_time=datetime.strptime(end_time, "%H:%M").time(),
                is_active=is_active,
            )
            messages.success(request, "Availability saved.")
            return redirect("doctor_siddhartha:schedule")
        messages.error(request, "Please complete the availability form.")

    week_start = timezone.localdate() - timedelta(days=timezone.localdate().weekday())
    week_days = [week_start + timedelta(days=offset) for offset in range(7)]
    appointments = Appointment.objects.filter(doctor=request.user, appointment_date__range=(week_start, week_start + timedelta(days=6))).select_related("patient", "department").order_by("appointment_date", "appointment_time")

    context = {
        "doctor_profile": doctor_profile,
        "week_start": week_start,
        "week_days": week_days,
        "appointments": appointments,
        "availability_slots": DoctorAvailability.objects.filter(doctor=request.user).order_by("day_of_week", "start_time"),
    }
    return render(request, "doc_siddhartha/schedule.html", context)


@doctor_required
def patients_records(request):
    doctor_profile = _doctor_profile(request.user)
    patient_search = (request.GET.get("search") or "").strip()
    patients = Appointment.objects.filter(doctor=request.user).select_related("patient").order_by("-appointment_date", "-appointment_time")
    if patient_search:
        patients = patients.filter(Q(patient__first_name__icontains=patient_search) | Q(patient__last_name__icontains=patient_search) | Q(patient__username__icontains=patient_search))

    selected_patient_id = request.GET.get("patient")
    selected_patient_appointment = None
    if selected_patient_id:
        selected_patient_appointment = patients.filter(patient_id=selected_patient_id).first()
    if not selected_patient_appointment:
        selected_patient_appointment = patients.first()

    selected_patient = selected_patient_appointment.patient if selected_patient_appointment else None
    patient_records = MedicalRecord.objects.filter(patient=selected_patient).select_related("doctor", "department") if selected_patient else MedicalRecord.objects.none()
    patient_prescriptions = Prescription.objects.filter(patient=selected_patient).prefetch_related("items") if selected_patient else Prescription.objects.none()

    recent_patients = []
    seen_ids = set()
    for appointment in patients:
        if appointment.patient_id in seen_ids:
            continue
        recent_patients.append(appointment)
        seen_ids.add(appointment.patient_id)

    selected_patient_profile = (
        PatientProfile.objects.filter(user=selected_patient).first() if selected_patient else None
    )

    context = {
        "doctor_profile": doctor_profile,
        "patients": recent_patients,
        "selected_patient": selected_patient,
        "selected_patient_profile": selected_patient_profile,
        "selected_appointment": selected_patient_appointment,
        "patient_records": patient_records,
        "patient_prescriptions": patient_prescriptions,
    }
    return render(request, "doc_siddhartha/patients_records.html", context)


@doctor_required
def prescription(request):
    doctor_profile = _doctor_profile(request.user)
    selected_patient_id = request.GET.get("patient") or request.POST.get("patient_id")
    selected_patient = None
    if selected_patient_id:
        selected_patient = Appointment.objects.filter(doctor=request.user, patient_id=selected_patient_id).select_related("patient").first()
        if selected_patient:
            selected_patient = selected_patient.patient

    if request.method == "POST":
        diagnosis = (request.POST.get("diagnosis") or "").strip()
        notes = (request.POST.get("notes") or "").strip()
        patient_id = request.POST.get("patient_id")
        if patient_id and diagnosis:
            patient_appointment = Appointment.objects.filter(doctor=request.user, patient_id=patient_id).select_related("patient").first()
            if patient_appointment:
                prescription = Prescription.objects.create(
                    patient=patient_appointment.patient,
                    doctor=request.user,
                    appointment=patient_appointment,
                    diagnosis=diagnosis,
                    notes=notes,
                    prescribed_on=timezone.localdate(),
                    is_active=True,
                )
                medicines = request.POST.getlist("medicine_name")
                dosages = request.POST.getlist("dosage")
                frequencies = request.POST.getlist("frequency")
                durations = request.POST.getlist("duration")
                instructions = request.POST.getlist("instructions")
                for index, medicine_name in enumerate(medicines):
                    medicine_name = medicine_name.strip()
                    if not medicine_name:
                        continue
                    PrescriptionItem.objects.create(
                        prescription=prescription,
                        medicine_name=medicine_name,
                        dosage=(dosages[index] if index < len(dosages) else "").strip(),
                        frequency=(frequencies[index] if index < len(frequencies) else "").strip(),
                        duration=(durations[index] if index < len(durations) else "").strip(),
                        instructions=(instructions[index] if index < len(instructions) else "").strip(),
                    )
                messages.success(request, "Prescription saved successfully.")
                return redirect(f"{request.path}?patient={patient_id}")
        messages.error(request, "Select a patient and add a diagnosis before saving.")

    past_prescriptions = Prescription.objects.filter(doctor=request.user).select_related("patient").prefetch_related("items").order_by("-prescribed_on")
    selected_patient_prescription_count = (
        Prescription.objects.filter(doctor=request.user, patient=selected_patient).count()
        if selected_patient
        else past_prescriptions.count()
    )

    context = {
        "doctor_profile": doctor_profile,
        "selected_patient": selected_patient,
        "patients": Appointment.objects.filter(doctor=request.user).values("patient_id", "patient__first_name", "patient__last_name", "patient__username").distinct().order_by("patient__first_name", "patient__last_name"),
        "past_prescriptions": past_prescriptions,
        "selected_patient_prescription_count": selected_patient_prescription_count,
    }
    return render(request, "doc_siddhartha/prescription.html", context)
