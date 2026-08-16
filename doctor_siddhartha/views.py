from datetime import date, datetime, timedelta

from django.contrib import messages
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from admin_nishan.models import (
    Appointment,
    Department,
    DoctorAvailability,
    LabReport,
    MedicalRecord,
    Notification,
    Prescription,
    PrescriptionItem,
)
from hospital.access import doctor_required
from hospital.notifications import notify, notify_appointment
from hospital.reminders import build_reminders_for_prescription
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
    profiles_by_user = {
        profile.user_id: profile
        for profile in PatientProfile.objects.filter(user_id__in=list(patient_ids))
    }
    patients = []
    for patient_id in patient_ids:
        latest = Appointment.objects.filter(doctor=doctor_user, patient_id=patient_id).select_related("patient").order_by("-appointment_date", "-appointment_time").first()
        if latest:
            latest.patient_profile = profiles_by_user.get(patient_id)
            patients.append(latest)
    return patients


@doctor_required
def approve_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, doctor=request.user)
    if appointment.status != Appointment.STATUS_PENDING:
        messages.error(request, "This appointment is no longer pending.")
        return redirect("doctor_siddhartha:dashboard")
    appointment.status = Appointment.STATUS_CONFIRMED
    appointment.save(update_fields=["status"])
    notify_appointment(
        appointment.patient,
        "Appointment confirmed",
        f"Dr. {request.user.get_full_name() or request.user.username} confirmed your appointment on "
        f"{appointment.display_date} at {appointment.display_time}.",
        appointment=appointment,
    )
    messages.success(request, f"Appointment with {appointment.patient_name} has been confirmed.")
    return redirect("doctor_siddhartha:dashboard")


@doctor_required
def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id, doctor=request.user)
    if appointment.status != Appointment.STATUS_PENDING:
        messages.error(request, "This appointment is no longer pending.")
        return redirect("doctor_siddhartha:dashboard")
    appointment.status = Appointment.STATUS_CANCELLED
    appointment.save(update_fields=["status"])
    notify_appointment(
        appointment.patient,
        "Appointment cancelled",
        f"Dr. {request.user.get_full_name() or request.user.username} cancelled your appointment on "
        f"{appointment.display_date} at {appointment.display_time}.",
        appointment=appointment,
    )
    messages.warning(request, f"Appointment with {appointment.patient_name} has been rejected.")
    return redirect("doctor_siddhartha:dashboard")


@doctor_required
def doctor_dashboard(request):
    doctor_profile = _doctor_profile(request.user)
    today = timezone.localdate()
    todays_appointments = _today_schedule(request.user)
    pending_prescriptions = Prescription.objects.filter(doctor=request.user, is_active=True).count()
    total_patients = Appointment.objects.filter(doctor=request.user).values("patient_id").distinct().count()
    pending_appointments = (
        Appointment.objects.filter(doctor=request.user, status=Appointment.STATUS_PENDING)
        .select_related("patient", "department")
        .order_by("appointment_date", "appointment_time")
    )

    context = {
        "doctor_profile": doctor_profile,
        "total_patients": total_patients,
        "todays_appointments": todays_appointments.count(),
        "pending_prescriptions": pending_prescriptions,
        "today_schedule": todays_appointments,
        "recent_patients": _recent_patients(request.user),
        "notifications": Notification.objects.filter(recipient=request.user, is_read=False)[:5],
        "today_label": today.strftime("%A, %B %d"),
        "pending_appointments": pending_appointments,
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
    week_end = week_start + timedelta(days=6)
    week_days = [week_start + timedelta(days=offset) for offset in range(7)]
    appointments = Appointment.objects.filter(doctor=request.user, appointment_date__range=(week_start, week_start + timedelta(days=6))).select_related("patient", "department").order_by("appointment_date", "appointment_time")

    context = {
        "doctor_profile": doctor_profile,
        "week_start": week_start,
        "week_end": week_end,
        "week_days": week_days,
        "appointments": appointments,
        "availability_slots": DoctorAvailability.objects.filter(doctor=request.user).order_by("day_of_week", "start_time"),
    }
    return render(request, "doc_siddhartha/schedule.html", context)


@doctor_required
def edit_availability(request, slot_id):
    slot = get_object_or_404(DoctorAvailability, pk=slot_id, doctor=request.user)
    if request.method == "POST":
        day_of_week = request.POST.get("day_of_week")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        is_active = request.POST.get("is_active") == "on"
        if day_of_week and start_time and end_time:
            slot.day_of_week = int(day_of_week)
            slot.start_time = datetime.strptime(start_time, "%H:%M").time()
            slot.end_time = datetime.strptime(end_time, "%H:%M").time()
            slot.is_active = is_active
            slot.save(update_fields=["day_of_week", "start_time", "end_time", "is_active"])
            messages.success(request, "Availability updated.")
        else:
            messages.error(request, "Please complete the availability form.")
    return redirect("doctor_siddhartha:schedule")


@doctor_required
def delete_availability(request, slot_id):
    slot = get_object_or_404(DoctorAvailability, pk=slot_id, doctor=request.user)
    if request.method == "POST":
        slot.delete()
        messages.success(request, "Availability slot removed.")
    return redirect("doctor_siddhartha:schedule")


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

    # Attach each patient's profile so the list can render real avatars instead
    # of initials. One query for the whole page rather than one per row.
    profiles_by_user = {
        profile.user_id: profile
        for profile in PatientProfile.objects.filter(user_id__in=seen_ids)
    }
    for appointment in recent_patients:
        appointment.patient_profile = profiles_by_user.get(appointment.patient_id)

    selected_patient_profile = (
        profiles_by_user.get(selected_patient.id)
        if selected_patient
        else None
    )
    if selected_patient and selected_patient_profile is None:
        selected_patient_profile = PatientProfile.objects.filter(user=selected_patient).first()

    editing_record = None
    edit_record_id = request.GET.get("edit_record")
    if edit_record_id:
        editing_record = MedicalRecord.objects.filter(pk=edit_record_id, doctor=request.user).first()

    context = {
        "doctor_profile": doctor_profile,
        "patients": recent_patients,
        "selected_patient": selected_patient,
        "selected_patient_profile": selected_patient_profile,
        "selected_appointment": selected_patient_appointment,
        "patient_records": patient_records,
        "patient_prescriptions": patient_prescriptions,
        "editing_record": editing_record,
        "status_choices": MedicalRecord.STATUS_CHOICES,
    }
    return render(request, "doc_siddhartha/patients_records.html", context)


@doctor_required
def add_medical_record(request, patient_id):
    if request.method == "POST":
        diagnosis = (request.POST.get("diagnosis") or "").strip()
        symptoms = (request.POST.get("symptoms") or "").strip()
        treatment = (request.POST.get("treatment") or "").strip()
        notes = (request.POST.get("notes") or "").strip()
        status = request.POST.get("status") or MedicalRecord.STATUS_STABLE
        visit_date = request.POST.get("visit_date") or timezone.localdate().isoformat()
        follow_up_date = request.POST.get("follow_up_date") or None

        if diagnosis:
            doctor_profile = _doctor_profile(request.user)
            record = MedicalRecord.objects.create(
                patient_id=patient_id,
                doctor=request.user,
                department=doctor_profile.department,
                diagnosis=diagnosis,
                symptoms=symptoms,
                treatment=treatment,
                notes=notes,
                status=status,
                visit_date=visit_date,
                follow_up_date=follow_up_date or None,
            )
            notify(
                record.patient,
                "New medical record",
                f"Dr. {request.user.get_full_name() or request.user.username} added a record: {record.diagnosis}.",
                action_url="/patient/records/",
            )
            messages.success(request, "Medical record added.")
        else:
            messages.error(request, "Diagnosis is required to save a medical record.")
    return redirect(f"/doctor/patients/?patient={patient_id}")


@doctor_required
def edit_medical_record(request, record_id):
    record = get_object_or_404(MedicalRecord, pk=record_id, doctor=request.user)
    if request.method == "POST":
        record.diagnosis = (request.POST.get("diagnosis") or record.diagnosis).strip()
        record.symptoms = (request.POST.get("symptoms") or "").strip()
        record.treatment = (request.POST.get("treatment") or "").strip()
        record.notes = (request.POST.get("notes") or "").strip()
        record.status = request.POST.get("status") or record.status
        visit_date = request.POST.get("visit_date")
        if visit_date:
            record.visit_date = visit_date
        follow_up_date = request.POST.get("follow_up_date")
        record.follow_up_date = follow_up_date or None
        record.save()
        notify(
            record.patient,
            "Medical record updated",
            f"Dr. {request.user.get_full_name() or request.user.username} updated your record: {record.diagnosis}.",
            action_url="/patient/records/",
        )
        messages.success(request, "Medical record updated.")

        if request.POST.get("next") == "medical_records":
            return redirect("doctor_siddhartha:medical_records")
    return redirect(f"/doctor/patients/?patient={record.patient_id}")


@doctor_required
def prescription(request):
    doctor_profile = _doctor_profile(request.user)
    selected_patient_id = request.GET.get("patient") or request.POST.get("patient_id")
    selected_patient = None
    if selected_patient_id:
        selected_patient = Appointment.objects.filter(doctor=request.user, patient_id=selected_patient_id).select_related("patient").first()
        if selected_patient:
            selected_patient = selected_patient.patient

    editing_prescription = None
    edit_id = request.GET.get("edit")
    if edit_id:
        editing_prescription = Prescription.objects.filter(pk=edit_id, doctor=request.user).prefetch_related("items").first()

    if request.method == "POST":
        diagnosis = (request.POST.get("diagnosis") or "").strip()
        notes = (request.POST.get("notes") or "").strip()
        patient_id = request.POST.get("patient_id")
        prescription_id = request.POST.get("prescription_id")

        if patient_id and diagnosis:
            patient_appointment = Appointment.objects.filter(doctor=request.user, patient_id=patient_id).select_related("patient").first()
            if patient_appointment:
                if prescription_id:
                    rx = get_object_or_404(Prescription, pk=prescription_id, doctor=request.user)
                    rx.diagnosis = diagnosis
                    rx.notes = notes
                    rx.save(update_fields=["diagnosis", "notes", "updated_at"])
                    rx.items.all().delete()
                else:
                    rx = Prescription.objects.create(
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
                        prescription=rx,
                        medicine_name=medicine_name,
                        dosage=(dosages[index] if index < len(dosages) else "").strip(),
                        frequency=(frequencies[index] if index < len(frequencies) else "").strip(),
                        duration=(durations[index] if index < len(durations) else "").strip(),
                        instructions=(instructions[index] if index < len(instructions) else "").strip(),
                    )
                reminder_count = build_reminders_for_prescription(rx)
                doctor_label = request.user.get_full_name() or request.user.username
                if prescription_id:
                    notify(
                        rx.patient,
                        "Prescription updated",
                        f"Dr. {doctor_label} updated your prescription for {rx.diagnosis}.",
                        action_url="/patient/prescriptions/",
                    )
                else:
                    notify(
                        rx.patient,
                        "New prescription",
                        f"Dr. {doctor_label} prescribed medication for {rx.diagnosis}. "
                        f"{reminder_count} daily reminder(s) added.",
                        action_url="/patient/prescriptions/",
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
        "editing_prescription": editing_prescription,
    }
    return render(request, "doc_siddhartha/prescription.html", context)


@doctor_required
def edit_prescription(request, prescription_id):
    rx = get_object_or_404(Prescription, pk=prescription_id, doctor=request.user)
    return redirect(f"/doctor/prescriptions/?patient={rx.patient_id}&edit={prescription_id}")


@doctor_required
def delete_prescription(request, prescription_id):
    rx = get_object_or_404(Prescription, pk=prescription_id, doctor=request.user)
    if request.method == "POST":
        patient_id = rx.patient_id
        notify(
            rx.patient,
            "Prescription deleted",
            f"Dr. {request.user.get_full_name() or request.user.username} removed your prescription for {rx.diagnosis}.",
            action_url="/patient/prescriptions/",
        )
        rx.delete()
        messages.success(request, "Prescription deleted.")
        return redirect(f"/doctor/prescriptions/?patient={patient_id}")
    return redirect("doctor_siddhartha:prescriptions")


@doctor_required
def edit_profile(request):
    profile = _doctor_profile(request.user)
    if request.method == "POST":
        request.user.first_name = (request.POST.get("first_name") or "").strip()
        request.user.last_name = (request.POST.get("last_name") or "").strip()
        request.user.email = request.POST.get("email") or request.user.email
        request.user.save(update_fields=["first_name", "last_name", "email"])

        profile.specialization = (request.POST.get("specialization") or "").strip()
        profile.license_number = (request.POST.get("license_number") or "").strip()
        profile.phone = request.POST.get("phone") or profile.phone
        profile.experience_years = int(request.POST.get("experience_years") or 0)
        profile.bio = (request.POST.get("bio") or "").strip()

        if request.POST.get("remove_picture") == "1":
            profile.profile_picture.delete(save=False)
            profile.profile_picture = None
        elif request.FILES.get("profile_picture"):
            profile.profile_picture = request.FILES["profile_picture"]

        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("doctor_siddhartha:dashboard")

    context = {
        "profile": profile,
        "user": request.user,
        "departments": Department.objects.filter(is_active=True).order_by("name"),
    }
    return render(request, "doc_siddhartha/edit_profile.html", context)


@doctor_required
def medical_records(request):
    doctor_profile = _doctor_profile(request.user)
    records = MedicalRecord.objects.filter(doctor=request.user).select_related("patient", "department").order_by("-visit_date", "-created_at")
    patient_id = request.GET.get("patient")
    if patient_id:
        records = records.filter(patient_id=patient_id)

    editing_record = None
    edit_record_id = request.GET.get("edit_record")
    if edit_record_id:
        editing_record = MedicalRecord.objects.filter(pk=edit_record_id, doctor=request.user).first()

    context = {
        "doctor_profile": doctor_profile,
        "records": records,
        "selected_patient_id": patient_id,
        "editing_record": editing_record,
        "status_choices": MedicalRecord.STATUS_CHOICES,
    }
    return render(request, "doc_siddhartha/medical_records.html", context)


@doctor_required
def lab_reports(request):
    doctor_profile = _doctor_profile(request.user)
    reports = LabReport.objects.filter(doctor=request.user).select_related("patient").order_by("-ordered_on", "-created_at")
    patient_id = request.GET.get("patient")
    if patient_id:
        reports = reports.filter(patient_id=patient_id)
    context = {
        "doctor_profile": doctor_profile,
        "reports": reports,
        "selected_patient_id": patient_id,
    }
    return render(request, "doc_siddhartha/lab_reports.html", context)


@doctor_required
def notifications(request):
    context = {
        "doctor_profile": _doctor_profile(request.user),
        "notifications": Notification.objects.filter(recipient=request.user).order_by("-created_at"),
    }
    return render(request, "doc_siddhartha/notifications.html", context)


@doctor_required
def mark_all_read(request):
    if request.method == "POST":
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect("doctor_siddhartha:notifications")