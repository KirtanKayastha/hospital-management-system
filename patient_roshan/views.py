import calendar
from datetime import date, datetime, time, timedelta
from types import SimpleNamespace

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from admin_nishan.models import Appointment, BillingInvoice, Department, LabReport, MedicalRecord, Notification, Prescription
from doctor_siddhartha.models import DoctorProfile
from hospital.access import ensure_patient_profile, patient_required
from .models import PatientProfile


WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _default_department():
    department, _ = Department.objects.get_or_create(
        slug="general-medicine",
        defaults={"name": "General Medicine", "description": "General patient care and triage."},
    )
    return department


def _initials(name):
    parts = (name or "").split()
    if not parts:
        return "U"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return f"{parts[0][0]}{parts[-1][0]}".upper()


def _doctor_card(profile):
    user = profile.user
    availability = profile.user.availability_slots.filter(is_active=True).order_by("day_of_week", "start_time")
    review_count = user.doctor_appointments.filter(status=Appointment.STATUS_COMPLETED).count()
    rating = round(min(5.0, 4.0 + (review_count * 0.1)), 1) if review_count else 0.0
    available_slots = [f"{slot.day_label[:3]} {slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}" for slot in availability]
    available_days = ", ".join(dict(availability.model.DAY_CHOICES).get(slot.day_of_week, str(slot.day_of_week)) for slot in availability)
    return {
        "id": profile.user_id,
        "initials": profile.initials,
        "name": profile.display_name,
        "specialization": profile.specialization or profile.department.name,
        "experience": profile.experience_years,
        "rating": rating,
        "review_count": review_count,
        "available_slots": available_slots,
        "available_days": available_days or "No regular availability set",
        "department_id": profile.department_id,
        "department_name": profile.department.name,
    }


def _calendar_days(selected_date):
    year = selected_date.year
    month = selected_date.month
    first_day_weekday, days_in_month = calendar.monthrange(year, month)
    days = []
    today = timezone.localdate()

    for day_number in range(1, days_in_month + 1):
        current_date = date(year, month, day_number)
        days.append(
            {
                "number": day_number,
                "date": current_date.isoformat(),
                "is_past": current_date < today,
                "is_selected": current_date == selected_date,
            }
        )

    padding = [{"number": "", "date": "", "is_past": True, "is_selected": False} for _ in range(first_day_weekday)]
    return padding + days


def _time_slots(selected_date, doctor_id=None):
    start_hour = 9
    end_hour = 17
    slots = []
    booked_times = set()

    if doctor_id:
        booked_times = set(
            Appointment.objects.filter(
                doctor_id=doctor_id,
                appointment_date=selected_date,
                status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED],
            ).values_list("appointment_time", flat=True)
        )

    current_time = time(start_hour, 0)
    while current_time < time(end_hour, 0):
        slots.append(
            {
                "value": current_time.strftime("%H:%M"),
                "label": current_time.strftime("%I:%M %p"),
                "is_booked": current_time in booked_times,
            }
        )
        slot_datetime = datetime.combine(date.today(), current_time) + timedelta(minutes=30)
        current_time = slot_datetime.time()

    return slots


def _patient_profile(user):
    return ensure_patient_profile(user)


@patient_required
def dashboard(request):
    profile = _patient_profile(request.user)
    today = timezone.localdate()

    recent_appointments = (
        Appointment.objects.filter(patient=request.user)
        .select_related("doctor", "department")
        .order_by("-appointment_date", "-appointment_time")[:4]
    )
    prescriptions = (
        Prescription.objects.filter(patient=request.user, is_active=True)
        .prefetch_related("items")
        .select_related("doctor")
        .order_by("-prescribed_on")[:4]
    )

    context = {
        "active_page": "dashboard",
        "patient": profile,
        "upcoming_count": Appointment.objects.filter(
            patient=request.user,
            appointment_date__gte=today,
            status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED],
        ).count(),
        "total_visits": Appointment.objects.filter(patient=request.user, status=Appointment.STATUS_COMPLETED).count(),
        "records_count": MedicalRecord.objects.filter(patient=request.user).count(),
        "recent_appointments": recent_appointments,
        "prescriptions": prescriptions,
        "notifications": Notification.objects.filter(recipient=request.user, is_read=False)[:5],
    }
    return render(request, "patient_roshan/dashboard.html", context)


@patient_required
def book_appointment(request):
    profile = _patient_profile(request.user)
    selected_doctor_id = request.POST.get("doctor_id") or request.GET.get("doctor") or ""
    selected_date_value = request.POST.get("appointment_date") or request.GET.get("date")
    selected_time_value = request.POST.get("appointment_time") or request.GET.get("time") or ""

    if selected_date_value:
        try:
            selected_date = date.fromisoformat(selected_date_value)
        except ValueError:
            selected_date = timezone.localdate() + timedelta(days=1)
    else:
        selected_date = timezone.localdate() + timedelta(days=1)

    if request.method == "POST":
        doctor_id = request.POST.get("doctor_id")
        appointment_date_value = request.POST.get("appointment_date")
        appointment_time_value = request.POST.get("appointment_time")
        reason = (request.POST.get("reason") or "").strip()

        errors = []
        if not doctor_id:
            errors.append("Select a doctor before booking.")
        if not appointment_date_value:
            errors.append("Select an appointment date.")
        if not appointment_time_value:
            errors.append("Select an appointment time.")
        if not reason:
            errors.append("Add a reason for the visit.")

        try:
            appointment_date = date.fromisoformat(appointment_date_value)
        except (TypeError, ValueError):
            appointment_date = None
            if not errors:
                errors.append("Select a valid appointment date.")

        try:
            appointment_time = datetime.strptime(appointment_time_value, "%H:%M").time()
        except (TypeError, ValueError):
            appointment_time = None
            if not errors:
                errors.append("Select a valid appointment time.")

        doctor_profile = None
        if doctor_id:
            doctor_profile = DoctorProfile.objects.select_related("user", "department").filter(user_id=doctor_id).first()
            if not doctor_profile:
                errors.append("Selected doctor does not exist.")

        if appointment_date and appointment_date < timezone.localdate():
            errors.append("Appointment date cannot be in the past.")

        if doctor_profile and appointment_date and appointment_time:
            if Appointment.objects.filter(
                doctor=doctor_profile.user,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED],
            ).exists():
                errors.append("That time slot is already booked.")

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            appointment = Appointment.objects.create(
                patient=request.user,
                doctor=doctor_profile.user,
                department=doctor_profile.department,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason=reason,
                status=Appointment.STATUS_PENDING,
            )
            Notification.objects.create(
                recipient=request.user,
                title="Appointment booked",
                message=f"Your appointment with {appointment.doctor_name} on {appointment.display_date} at {appointment.display_time} is pending confirmation.",
                category=Notification.CATEGORY_APPOINTMENT,
                action_url=f"/patient/appointments/{appointment.id}/",
            )
            Notification.objects.create(
                recipient=appointment.doctor,
                title="New appointment request",
                message=f"{appointment.patient_name} requested an appointment on {appointment.display_date} at {appointment.display_time}.",
                category=Notification.CATEGORY_APPOINTMENT,
                action_url=f"/doctor/schedule/",
            )
            messages.success(request, "Appointment booked successfully.")
            return redirect("patient_roshan:my_appointments")

    doctors = [
        _doctor_card(profile)
        for profile in DoctorProfile.objects.select_related("user", "department").filter(status=DoctorProfile.STATUS_ACTIVE)
    ]
    departments = Department.objects.filter(is_active=True).order_by("name")
    selected_date = selected_date if selected_date else timezone.localdate() + timedelta(days=1)

    context = {
        "active_page": "book",
        "patient": profile,
        "departments": departments,
        "doctors": doctors,
        "time_slots": _time_slots(selected_date, selected_doctor_id or None),
        "calendar_days": _calendar_days(selected_date),
        "selected_date": selected_date.isoformat(),
        "selected_time": selected_time_value,
        "selected_doctor_id": int(selected_doctor_id) if str(selected_doctor_id).isdigit() else "",
    }
    return render(request, "patient_roshan/book_appointment.html", context)


@patient_required
def find_doctor(request):
    department_id = request.GET.get("department", "")
    search = (request.GET.get("search", "") or "").strip()
    availability = request.GET.get("availability", "")

    doctor_profiles = DoctorProfile.objects.select_related("user", "department").filter(status=DoctorProfile.STATUS_ACTIVE)
    if department_id:
        doctor_profiles = doctor_profiles.filter(department_id=department_id)
    if search:
        doctor_profiles = doctor_profiles.filter(
            Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(user__username__icontains=search)
            | Q(specialization__icontains=search)
        )

    if availability in {"today", "week"}:
        target_days = [timezone.localdate().weekday()]
        if availability == "week":
            target_days = list(range(7))
        doctor_profiles = doctor_profiles.filter(user__availability_slots__day_of_week__in=target_days, user__availability_slots__is_active=True).distinct()

    doctors = [_doctor_card(profile) for profile in doctor_profiles]

    context = {
        "active_page": "finddoctor",
        "patient": _patient_profile(request.user),
        "departments": Department.objects.filter(is_active=True).order_by("name"),
        "doctors": doctors,
    }
    return render(request, "patient_roshan/find_doctor.html", context)


@patient_required
def my_appointments(request):
    status_filter = request.GET.get("status", "")
    search = (request.GET.get("search", "") or "").strip()

    appointments = Appointment.objects.filter(patient=request.user).select_related("doctor", "department")
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    if search:
        appointments = appointments.filter(
            Q(doctor__first_name__icontains=search)
            | Q(doctor__last_name__icontains=search)
            | Q(doctor__username__icontains=search)
            | Q(department__name__icontains=search)
        )

    paginator = Paginator(appointments, 10)
    page_number = request.GET.get("page", 1)
    appointments_page = paginator.get_page(page_number)

    status_filters = [
        {"label": "All", "value": ""},
        {"label": "Confirmed", "value": Appointment.STATUS_CONFIRMED},
        {"label": "Pending", "value": Appointment.STATUS_PENDING},
        {"label": "Completed", "value": Appointment.STATUS_COMPLETED},
        {"label": "Cancelled", "value": Appointment.STATUS_CANCELLED},
    ]

    context = {
        "active_page": "appointments",
        "patient": _patient_profile(request.user),
        "appointments": appointments_page,
        "status_filters": status_filters,
        "current_status": status_filter,
    }
    return render(request, "patient_roshan/my_appointments.html", context)


@patient_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    appointment.status = Appointment.STATUS_CANCELLED
    appointment.save(update_fields=["status", "updated_at"])
    Notification.objects.create(
        recipient=request.user,
        title="Appointment cancelled",
        message=f"Your appointment with {appointment.doctor_name} on {appointment.display_date} was cancelled.",
        category=Notification.CATEGORY_APPOINTMENT,
        action_url=f"/patient/appointments/{appointment.id}/",
    )
    messages.success(request, "Appointment cancelled.")
    return redirect("patient_roshan:my_appointments")


@patient_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    return redirect(
        f"/patient/book/?doctor={appointment.doctor_id}&date={appointment.appointment_date.isoformat()}&time={appointment.appointment_time.strftime('%H:%M')}"
    )


@patient_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment.objects.select_related("doctor", "department"), id=appointment_id, patient=request.user)
    medical_record = getattr(appointment, "medical_record", None)
    prescription = getattr(appointment, "prescription", None)

    context = {
        "active_page": "appointments",
        "patient": _patient_profile(request.user),
        "appointment": appointment,
        "medical_record": medical_record,
        "prescription": prescription,
    }
    return render(request, "patient_roshan/appointment_detail.html", context)


@patient_required
def medical_records(request):
    profile = _patient_profile(request.user)
    records = MedicalRecord.objects.filter(patient=request.user).select_related("doctor", "department").order_by("-visit_date", "-created_at")
    context = {
        "active_page": "records",
        "patient": profile,
        "records": records,
    }
    return render(request, "patient_roshan/medical_records.html", context)


@patient_required
def lab_reports(request):
    context = {
        "active_page": "labreports",
        "patient": _patient_profile(request.user),
        "lab_reports": LabReport.objects.filter(patient=request.user).select_related("doctor", "appointment").order_by("-ordered_on", "-created_at"),
    }
    return render(request, "patient_roshan/lab_reports.html", context)


@patient_required
def profile(request):
    patient = _patient_profile(request.user)
    if request.method == "POST":
        full_name = (request.POST.get("full_name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        dob = request.POST.get("dob") or None
        gender = request.POST.get("gender") or ""
        blood_group = request.POST.get("blood_group") or ""
        address = (request.POST.get("address") or "").strip()

        if full_name:
            name_parts = full_name.split(maxsplit=1)
            request.user.first_name = name_parts[0]
            request.user.last_name = name_parts[1] if len(name_parts) > 1 else ""
        request.user.email = email or request.user.email
        request.user.save(update_fields=["first_name", "last_name", "email"])

        patient.phone = phone
        patient.gender = gender
        patient.blood_group = blood_group
        patient.address = address
        patient.dob = dob or None
        patient.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("patient_roshan:profile")

    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    context = {
        "active_page": "profile",
        "patient": patient,
        "blood_groups": blood_groups,
    }
    return render(request, "patient_roshan/profile.html", context)


@patient_required
def update_emergency_contact(request):
    patient = _patient_profile(request.user)
    if request.method == "POST":
        patient.emergency_contact_name = request.POST.get("emergency_name", "").strip()
        patient.emergency_contact_relation = request.POST.get("emergency_relation", "").strip()
        patient.emergency_contact_phone = request.POST.get("emergency_phone", "").strip()
        patient.save()
        messages.success(request, "Emergency contact updated.")
    return redirect("patient_roshan:profile")


@patient_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password") or ""
        new_password = request.POST.get("new_password") or ""
        if not request.user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("patient_roshan:profile")
        if len(new_password) < 8:
            messages.error(request, "New password must be at least 8 characters long.")
            return redirect("patient_roshan:profile")
        request.user.set_password(new_password)
        request.user.save(update_fields=["password"])
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password updated successfully.")
    return redirect("patient_roshan:profile")