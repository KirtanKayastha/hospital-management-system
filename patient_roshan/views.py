import base64
import hashlib
import hmac
import json
import uuid
from django.conf import settings as django_settings
from django.views.decorators.csrf import csrf_exempt
import calendar
from datetime import date, datetime, time, timedelta
from types import SimpleNamespace

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from admin_nishan.models import Appointment, BillingInvoice, Department, DoctorAvailability, LabReport, MedicalRecord, MedicineReminder, Notification, Prescription
from doctor_siddhartha.models import DoctorProfile
from hospital.access import ensure_patient_profile, patient_required
from .models import PatientProfile, PaymentTransaction


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
    availability = user.availability_slots.filter(is_active=True).order_by("day_of_week", "start_time")
    review_count = user.doctor_appointments.filter(status=Appointment.STATUS_COMPLETED).count()
    rating = round(min(5.0, 4.0 + (review_count * 0.1)), 1) if review_count else 0.0
    available_slots = [f"{slot.day_label[:3]} {slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}" for slot in availability]
    available_days = ", ".join(dict(availability.model.DAY_CHOICES).get(slot.day_of_week, str(slot.day_of_week)) for slot in availability)
    return {
        "id": user.id,
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
        "has_profile_picture": bool(profile.profile_picture),
        "profile_picture_url": profile.profile_picture.url if profile.profile_picture else "",
    }


def _availability_for_date(doctor_user, target_date):
    return DoctorAvailability.objects.filter(
        doctor=doctor_user,
        is_active=True,
        day_of_week=target_date.weekday(),
    ).order_by("start_time")


def _doctor_cards_for_booking(department_id="", search=""):
    doctor_profiles = DoctorProfile.objects.select_related("user", "department").filter(
        user__availability_slots__is_active=True,
    )
    if department_id:
        doctor_profiles = doctor_profiles.filter(department_id=department_id)
    if search:
        doctor_profiles = doctor_profiles.filter(
            Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(user__username__icontains=search)
            | Q(specialization__icontains=search)
        )
    return doctor_profiles.distinct()


def _build_time_slots(doctor_user, target_date):
    booked_times = set(
        Appointment.objects.filter(
            doctor=doctor_user,
            appointment_date=target_date,
            status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED],
        ).values_list("appointment_time", flat=True)
    )
    slots = []
    for availability in _availability_for_date(doctor_user, target_date):
        current_time = datetime.combine(target_date, availability.start_time)
        end_time = datetime.combine(target_date, availability.end_time)
        while current_time + timedelta(minutes=30) <= end_time:
            slot_time = current_time.time()
            slot_value = slot_time.strftime("%H:%M")
            slots.append({
                "value": slot_value,
                "label": slot_time.strftime("%I:%M %p"),
                "is_booked": slot_time in booked_times,
            })
            current_time += timedelta(minutes=30)
    return slots


def _calendar_days(selected_date):
    year = selected_date.year
    month = selected_date.month
    first_day_weekday, days_in_month = calendar.monthrange(year, month)
    days = []
    today = timezone.localdate()
    for day_number in range(1, days_in_month + 1):
        current_date = date(year, month, day_number)
        days.append({
            "number": day_number,
            "date": current_date.isoformat(),
            "is_past": current_date < today,
            "is_selected": current_date == selected_date,
        })
    padding = [{"number": "", "date": "", "is_past": True, "is_selected": False} for _ in range(first_day_weekday)]
    return padding + days


def _time_slots(selected_date, doctor_id=None):
    if not doctor_id:
        return []
    doctor_profile = DoctorProfile.objects.filter(user_id=doctor_id).select_related("user", "department").first()
    if not doctor_profile:
        return []
    return _build_time_slots(doctor_profile.user, selected_date)


@patient_required
def get_time_slots(request):
    doctor_id = request.GET.get("doctor_id", "")
    date_str = request.GET.get("date", "")
    if not doctor_id or not date_str:
        return render(request, "patient_roshan/_time_slots.html", {"time_slots": [], "selected_time": ""})
    try:
        selected_date = date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return render(request, "patient_roshan/_time_slots.html", {"time_slots": [], "selected_time": ""})
    time_slots = _time_slots(selected_date, doctor_id)
    selected_time = request.GET.get("time", "")
    return render(request, "patient_roshan/_time_slots.html", {
        "time_slots": time_slots,
        "selected_time": selected_time,
    })


def _patient_profile(user):
    return ensure_patient_profile(user)


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

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


# ─── BOOK APPOINTMENT ────────────────────────────────────────────────────────

@patient_required
def book_appointment(request):
    profile = _patient_profile(request.user)
    selected_doctor_id = request.POST.get("doctor_id") or request.GET.get("doctor") or ""
    selected_date_value = request.POST.get("appointment_date") or request.GET.get("date")
    selected_time_value = request.POST.get("appointment_time") or request.GET.get("time") or ""
    department_id = request.GET.get("department", "")
    search = (request.GET.get("search", "") or "").strip()
    form_errors = []

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

        if not doctor_id:
            form_errors.append("Select a doctor before booking.")
        if not appointment_date_value:
            form_errors.append("Select an appointment date.")
        if not appointment_time_value:
            form_errors.append("Select an appointment time.")
        if not reason:
            form_errors.append("Add a reason for the visit.")

        try:
            appointment_date = date.fromisoformat(appointment_date_value)
        except (TypeError, ValueError):
            appointment_date = None
            if not form_errors:
                form_errors.append("Select a valid appointment date.")

        try:
            appointment_time = datetime.strptime(appointment_time_value, "%H:%M").time()
        except (TypeError, ValueError):
            appointment_time = None
            if not form_errors:
                form_errors.append("Select a valid appointment time.")

        doctor_profile = None
        if doctor_id:
            doctor_profile = DoctorProfile.objects.select_related("user", "department").filter(user_id=doctor_id).first()
            if not doctor_profile:
                form_errors.append("Selected doctor does not exist.")
        else:
            form_errors.append("Select a doctor before booking.")

        if appointment_date and appointment_date < timezone.localdate():
            form_errors.append("Appointment date cannot be in the past.")

        if doctor_profile and appointment_date and appointment_time:
            available_values = {slot["value"] for slot in _build_time_slots(doctor_profile.user, appointment_date)}
            if appointment_time.strftime("%H:%M") not in available_values:
                form_errors.append("Selected time is not available for that doctor.")
            if Appointment.objects.filter(
                doctor=doctor_profile.user,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED],
            ).exists():
                form_errors.append("That time slot is already booked.")

        if not form_errors:
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
            return redirect("/patient/appointments/?booked=1")

    doctor_profiles = _doctor_cards_for_booking(department_id=department_id, search=search)
    doctors = [_doctor_card(profile) for profile in doctor_profiles]
    departments = Department.objects.filter(is_active=True).order_by("name")
    selected_date = selected_date if selected_date else timezone.localdate() + timedelta(days=1)

    if selected_doctor_id and not doctor_profiles.filter(user_id=selected_doctor_id).exists():
        selected_doctor_id = ""
    if not selected_doctor_id and doctor_profiles.exists():
        selected_doctor_profile = doctor_profiles.filter(user__availability_slots__day_of_week=selected_date.weekday()).first()
        if not selected_doctor_profile:
            selected_doctor_profile = doctor_profiles.first()
        selected_doctor_id = str(selected_doctor_profile.user_id)

    selected_doctor_profile = None
    if selected_doctor_id and str(selected_doctor_id).isdigit():
        selected_doctor_profile = DoctorProfile.objects.select_related("user", "department").filter(user_id=selected_doctor_id).first()
    if selected_doctor_profile and not _availability_for_date(selected_doctor_profile.user, selected_date).exists():
        alternate_doctor = doctor_profiles.filter(user__availability_slots__day_of_week=selected_date.weekday()).first()
        if alternate_doctor:
            selected_doctor_profile = alternate_doctor
            selected_doctor_id = str(alternate_doctor.user_id)

    time_slots = _build_time_slots(selected_doctor_profile.user, selected_date) if selected_doctor_profile else []
    available_time_values = {slot["value"] for slot in time_slots}
    if selected_time_value and selected_time_value not in available_time_values:
        selected_time_value = ""
    if not selected_time_value and time_slots:
        selected_time_value = time_slots[0]["value"]

    context = {
        "active_page": "book",
        "patient": profile,
        "departments": departments,
        "doctors": doctors,
        "time_slots": time_slots,
        "calendar_days": _calendar_days(selected_date),
        "selected_date": selected_date if isinstance(selected_date, str) else selected_date.isoformat(),
        "selected_time": selected_time_value,
        "selected_doctor_id": int(selected_doctor_id) if str(selected_doctor_id).isdigit() else "",
        "search": search,
        "selected_department_id": department_id,
        "form_errors": form_errors,
        "min_date": timezone.localdate().isoformat(),
        "max_date": (timezone.localdate() + timedelta(days=30)).isoformat(),
    }
    return render(request, "patient_roshan/book_appointment.html", context)


# ─── FIND DOCTOR ─────────────────────────────────────────────────────────────

@patient_required
def find_doctor(request):
    department_id = request.GET.get("department", "")
    search = (request.GET.get("search", "") or "").strip()
    availability = request.GET.get("availability", "")

    doctor_profiles = DoctorProfile.objects.select_related("user", "department").filter(
        user__availability_slots__is_active=True,
    )
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
        doctor_profiles = doctor_profiles.filter(
            user__availability_slots__day_of_week__in=target_days,
            user__availability_slots__is_active=True
        ).distinct()

    doctors = []
    for prof in doctor_profiles.distinct():
        doctor_card = _doctor_card(prof)
        doctor_card["available_slots"] = [
            f"{slot.get_day_of_week_display()[:3]} {slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}"
            for slot in prof.user.availability_slots.filter(is_active=True).order_by("day_of_week", "start_time")
        ]
        doctors.append(doctor_card)

    context = {
        "active_page": "finddoctor",
        "patient": _patient_profile(request.user),
        "departments": Department.objects.filter(is_active=True).order_by("name"),
        "doctors": doctors,
    }
    return render(request, "patient_roshan/find_doctor.html", context)


# ─── MY APPOINTMENTS ─────────────────────────────────────────────────────────

@patient_required
def my_appointments(request):
    status_filter = request.GET.get("status", "")
    search = (request.GET.get("search", "") or "").strip()
    booking_success = request.GET.get("booked") == "1"

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
        "booking_success": booking_success,
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
    appointment = get_object_or_404(
        Appointment.objects.select_related("doctor", "department"),
        id=appointment_id,
        patient=request.user
    )
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


# ─── MEDICAL RECORDS ─────────────────────────────────────────────────────────

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


# ─── LAB REPORTS ─────────────────────────────────────────────────────────────




# ─── PROFILE ─────────────────────────────────────────────────────────────────

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
        if request.FILES.get('profile_picture'):
            patient.profile_picture = request.FILES['profile_picture']
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
        confirm_password = request.POST.get("confirm_password") or ""
        if not request.user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("patient_roshan:settings")
        if len(new_password) < 8:
            messages.error(request, "New password must be at least 8 characters.")
            return redirect("patient_roshan:settings")
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("patient_roshan:settings")
        request.user.set_password(new_password)
        request.user.save(update_fields=["password"])
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password updated successfully.")
    return redirect("patient_roshan:settings")


# ─── PRESCRIPTIONS ───────────────────────────────────────────────────────────

@patient_required
def prescriptions(request):
    presc_list = Prescription.objects.filter(
        patient=request.user, is_active=True
    ).select_related('doctor').order_by('-prescribed_on')
    context = {
        'active_page': 'prescriptions',
        'patient': _patient_profile(request.user),
        'prescriptions': presc_list,
    }
    return render(request, 'patient_roshan/prescriptions.html', context)


# ─── BILLING ─────────────────────────────────────────────────────────────────

@patient_required
def billing(request):
    invoices = BillingInvoice.objects.filter(patient=request.user).order_by('-created_at')
    pending_count = invoices.filter(status='unpaid').count()
    context = {
        'active_page': 'billing',
        'patient': _patient_profile(request.user),
        'invoices': invoices,
        'pending_count': pending_count,
    }
    return render(request, 'patient_roshan/billing.html', context)


@patient_required
def invoices(request):
    invoices_qs = BillingInvoice.objects.filter(patient=request.user).order_by('-issued_on', '-created_at')
    context = {
        'active_page': 'invoices',
        'patient': _patient_profile(request.user),
        'invoices': invoices_qs,
    }
    return render(request, 'patient_roshan/invoices.html', context)


# ─── MESSAGES ────────────────────────────────────────────────────────────────




# ─── NOTIFICATIONS ───────────────────────────────────────────────────────────

@patient_required
def notifications(request):
    notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    context = {
        'active_page': 'notifications',
        'patient': _patient_profile(request.user),
        'notifications': notifs,
    }
    return render(request, 'patient_roshan/notifications.html', context)


@patient_required
def mark_all_read(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect('patient_roshan:notifications')


# ─── SETTINGS ────────────────────────────────────────────────────────────────

@patient_required
def settings(request):
    patient = _patient_profile(request.user)
    context = {
        'active_page': 'settings',
        'patient': patient,
        'preferences': patient,
    }
    return render(request, 'patient_roshan/settings.html', context)


@patient_required
def save_notification_preferences(request):
    if request.method == 'POST':
        patient = _patient_profile(request.user)
        patient.email_notifications = 'email_notifications' in request.POST
        patient.sms_reminders = 'sms_reminders' in request.POST
        patient.appointment_alerts = 'appointment_alerts' in request.POST
        patient.lab_notifications = 'lab_notifications' in request.POST
        patient.save()
        messages.success(request, 'Notification preferences saved.')
    return redirect('patient_roshan:settings')


@patient_required
def save_language(request):
    if request.method == 'POST':
        patient = _patient_profile(request.user)
        patient.language = request.POST.get('language', 'en')
        patient.save()
        messages.success(request, 'Language preference saved.')
    return redirect('patient_roshan:settings')


@patient_required
def save_privacy(request):
    if request.method == 'POST':
        patient = _patient_profile(request.user)
        patient.profile_visibility = request.POST.get('profile_visibility', 'doctors')
        patient.share_records = 'share_records' in request.POST
        patient.save()
        messages.success(request, 'Privacy settings saved.')
    return redirect('patient_roshan:settings')


@patient_required
def deactivate_account(request):
    if request.method == 'POST':
        request.user.is_active = False
        request.user.save()
        messages.success(request, 'Account deactivated.')
        return redirect('auth_kirtan:logout')
    return redirect('patient_roshan:settings')


@patient_required
def request_deletion(request):
    if request.method == 'POST':
        Notification.objects.create(
            recipient=request.user,
            title='Data deletion requested',
            message=f'Patient {request.user.get_full_name()} has requested account deletion.',
            category=Notification.CATEGORY_GENERAL,
        )
        messages.success(request, 'Your deletion request has been sent to admin.')
    return redirect('patient_roshan:settings')


@patient_required
def delete_account(request):
    if request.method == 'POST':
        username = request.user.username
        request.user.delete()
        messages.success(request, f'Account "{username}" has been permanently deleted.')
        return redirect('auth_kirtan:logout')
    return redirect('patient_roshan:settings')


@patient_required
def medicine_reminders(request):
    patient_profile = _patient_profile(request.user)
    today = timezone.localdate()
    reminders = (
        MedicineReminder.objects.filter(patient=request.user, is_active=True)
        .select_related('item', 'item__prescription')
        .order_by('remind_at')
    )
    active = [r for r in reminders if r.end_date is None or r.end_date >= today]
    context = {
        'patient_profile': patient_profile,
        'reminders': active,
        'taken_count': sum(1 for r in active if r.taken_today),
        'today': today,
        'active_page': 'reminders',
        'patient': patient_profile,
    }
    return render(request, 'patient_roshan/medicine_reminders.html', context)


@patient_required
def mark_medicine_taken(request, reminder_id):
    reminder = get_object_or_404(MedicineReminder, pk=reminder_id, patient=request.user)
    if request.method == 'POST':
        reminder.last_taken_on = timezone.localdate()
        reminder.save(update_fields=['last_taken_on'])
        messages.success(request, f'{reminder.medicine_name} marked as taken.')
    return redirect('patient_roshan:medicine_reminders')


@patient_required
def pay_at_counter(request, invoice_id):
    invoice = get_object_or_404(BillingInvoice, id=invoice_id, patient=request.user)
    if request.method == 'POST':
        invoice.status = 'pending_counter'
        invoice.save()
        Notification.objects.create(
            recipient=request.user,
            title='Counter payment selected',
            message=f'Please visit the billing counter to pay Rs. {invoice.amount} for invoice {invoice.invoice_number}.',
            category=Notification.CATEGORY_GENERAL,
            action_url='/patient/billing/',
        )
        messages.success(request, 'Please visit the hospital billing counter to complete payment.')
    return redirect('patient_roshan:billing')

# ─── PAYMENT ─────────────────────────────────────────────────────────────────

def _esewa_signature(message):
    key = django_settings.ESEWA_SECRET_KEY.encode()
    digest = hmac.new(key, message.encode(), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


@patient_required
def pay_online(request, invoice_id):
    invoice = get_object_or_404(BillingInvoice, id=invoice_id, patient=request.user)

    if invoice.status == 'paid':
        messages.info(request, 'This invoice is already paid.')
        return redirect('patient_roshan:billing')

    context = {
        'active_page': 'billing',
        'patient': _patient_profile(request.user),
        'invoice': invoice,
    }
    return render(request, 'patient_roshan/payment_gateway.html', context)


@patient_required
def esewa_initiate(request, invoice_id):
    invoice = get_object_or_404(BillingInvoice, id=invoice_id, patient=request.user)

    transaction_uuid = f"HMS-{invoice.id}-{uuid.uuid4().hex[:10]}"
    total_amount = f"{invoice.amount:.0f}"
    product_code = django_settings.ESEWA_PRODUCT_CODE

    PaymentTransaction.objects.create(
        user=request.user,
        invoice_id=invoice.id,
        transaction_uuid=transaction_uuid,
        gateway='esewa',
        amount=invoice.amount,
        status=PaymentTransaction.STATUS_INITIATED,
    )

    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    signature = _esewa_signature(message)

    base = django_settings.SITE_BASE_URL.rstrip('/')

    context = {
        'form_url': django_settings.ESEWA_FORM_URL,
        'amount': total_amount,
        'tax_amount': '0',
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': product_code,
        'product_service_charge': '0',
        'product_delivery_charge': '0',
        'success_url': f"{base}/patient/billing/esewa/verify/",
        'failure_url': f"{base}/patient/billing/esewa/failed/",
        'signed_field_names': 'total_amount,transaction_uuid,product_code',
        'signature': signature,
    }
    return render(request, 'patient_roshan/esewa_redirect.html', context)


@csrf_exempt
def esewa_verify(request):
    encoded = request.GET.get('data')
    if not encoded:
        messages.error(request, 'No payment data received from eSewa.')
        return redirect('patient_roshan:billing')

    try:
        decoded = json.loads(base64.b64decode(encoded).decode())
    except Exception:
        messages.error(request, 'Could not read the eSewa response.')
        return redirect('patient_roshan:billing')

    signed_fields = decoded.get('signed_field_names', '')
    message = ','.join(f"{f}={decoded.get(f, '')}" for f in signed_fields.split(','))
    expected = _esewa_signature(message)

    if not hmac.compare_digest(expected, decoded.get('signature', '')):
        messages.error(request, 'Payment signature verification failed.')
        return redirect('patient_roshan:billing')

    txn = PaymentTransaction.objects.filter(
        transaction_uuid=decoded.get('transaction_uuid')
    ).first()

    if not txn:
        messages.error(request, 'Transaction not found.')
        return redirect('patient_roshan:billing')

    if txn.status == PaymentTransaction.STATUS_COMPLETE:
        messages.info(request, 'This payment was already processed.')
        return redirect('patient_roshan:billing')

    if decoded.get('status') != 'COMPLETE':
        txn.status = PaymentTransaction.STATUS_FAILED
        txn.save()
        messages.error(request, 'Payment was not completed.')
        return redirect('patient_roshan:billing')

    invoice = BillingInvoice.objects.filter(id=txn.invoice_id, patient=txn.user).first()
    if not invoice:
        messages.error(request, 'Invoice not found.')
        return redirect('patient_roshan:billing')

    if abs(float(decoded.get('total_amount', '0').replace(',', '')) - float(invoice.amount)) > 0.01:
        txn.status = PaymentTransaction.STATUS_FAILED
        txn.save()
        messages.error(request, 'Payment amount did not match the invoice.')
        return redirect('patient_roshan:billing')

    txn.status = PaymentTransaction.STATUS_COMPLETE
    txn.gateway_ref = decoded.get('transaction_code', '')
    txn.save()

    invoice.status = 'paid'
    invoice.paid_on = timezone.localdate()
    invoice.save()

    Notification.objects.create(
        recipient=txn.user,
        title='Payment successful',
        message=f'Your eSewa payment of Rs. {invoice.amount} for invoice {invoice.invoice_number} was successful.',
        category=Notification.CATEGORY_GENERAL,
        action_url='/patient/billing/',
    )

    messages.success(request, f'Payment of Rs. {invoice.amount} completed via eSewa.')
    return redirect('patient_roshan:billing')


@csrf_exempt
def esewa_failed(request):
    messages.error(request, 'Payment was cancelled or failed. Please try again.')
    return redirect('patient_roshan:billing')


# ─── KHALTI ──────────────────────────────────────────────────────────────────

@patient_required
def khalti_initiate(request, invoice_id):
    import requests

    invoice = get_object_or_404(BillingInvoice, id=invoice_id, patient=request.user)

    if invoice.status == 'paid':
        messages.info(request, 'This invoice is already paid.')
        return redirect('patient_roshan:billing')

    purchase_order_id = f"HMS-{invoice.id}-{uuid.uuid4().hex[:10]}"
    amount_paisa = int(float(invoice.amount) * 100)
    base = django_settings.SITE_BASE_URL.rstrip('/')

    PaymentTransaction.objects.create(
        user=request.user,
        invoice_id=invoice.id,
        transaction_uuid=purchase_order_id,
        gateway='khalti',
        amount=invoice.amount,
        status=PaymentTransaction.STATUS_INITIATED,
    )

    payload = {
        "return_url": f"{base}/patient/billing/khalti/verify/",
        "website_url": base,
        "amount": amount_paisa,
        "purchase_order_id": purchase_order_id,
        "purchase_order_name": invoice.notes or f"Invoice {invoice.invoice_number}",
        "customer_info": {
            "name": request.user.get_full_name() or request.user.username,
            "email": request.user.email or "patient@hms.com",
            "phone": "9800000000",
        },
    }

    headers = {
        "Authorization": f"key {django_settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        res = requests.post(
            django_settings.KHALTI_INITIATE_URL,
            json=payload,
            headers=headers,
            timeout=15,
        )
        data = res.json()
    except Exception:
        messages.error(request, 'Could not reach Khalti. Please try again later.')
        return redirect('patient_roshan:billing')

    payment_url = data.get('payment_url')
    pidx = data.get('pidx')

    if not payment_url or not pidx:
        messages.error(request, f"Khalti error: {data.get('detail') or 'Could not start payment.'}")
        return redirect('patient_roshan:billing')

    PaymentTransaction.objects.filter(transaction_uuid=purchase_order_id).update(gateway_ref=pidx)

    return redirect(payment_url)


@csrf_exempt
def khalti_verify(request):
    import requests

    pidx = request.GET.get('pidx')
    if not pidx:
        messages.error(request, 'No payment reference received from Khalti.')
        return redirect('patient_roshan:billing')

    headers = {
        "Authorization": f"key {django_settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        res = requests.post(
            django_settings.KHALTI_LOOKUP_URL,
            json={"pidx": pidx},
            headers=headers,
            timeout=15,
        )
        data = res.json()
    except Exception:
        messages.error(request, 'Could not verify payment with Khalti.')
        return redirect('patient_roshan:billing')

    txn = PaymentTransaction.objects.filter(gateway_ref=pidx, gateway='khalti').first()
    if not txn:
        messages.error(request, 'Transaction not found.')
        return redirect('patient_roshan:billing')

    if txn.status == PaymentTransaction.STATUS_COMPLETE:
        messages.info(request, 'This payment was already processed.')
        return redirect('patient_roshan:billing')

    if data.get('status') != 'Completed':
        txn.status = PaymentTransaction.STATUS_FAILED
        txn.save()
        messages.error(request, f"Payment {data.get('status', 'failed')}. Please try again.")
        return redirect('patient_roshan:billing')

    invoice = BillingInvoice.objects.filter(id=txn.invoice_id, patient=txn.user).first()
    if not invoice:
        messages.error(request, 'Invoice not found.')
        return redirect('patient_roshan:billing')

    if abs(int(data.get('total_amount', 0)) - int(float(invoice.amount) * 100)) > 1:
        txn.status = PaymentTransaction.STATUS_FAILED
        txn.save()
        messages.error(request, 'Payment amount did not match the invoice.')
        return redirect('patient_roshan:billing')

    txn.status = PaymentTransaction.STATUS_COMPLETE
    txn.save()

    invoice.status = 'paid'
    invoice.paid_on = timezone.localdate()
    invoice.save()

    Notification.objects.create(
        recipient=txn.user,
        title='Payment successful',
        message=f'Your Khalti payment of Rs. {invoice.amount} for invoice {invoice.invoice_number} was successful.',
        category=Notification.CATEGORY_GENERAL,
        action_url='/patient/billing/',
    )

    messages.success(request, f'Payment of Rs. {invoice.amount} completed via Khalti.')
    return redirect('patient_roshan:billing')


@patient_required
def invoice_receipt(request, invoice_id):
    invoice = get_object_or_404(BillingInvoice, id=invoice_id, patient=request.user)
    txn = PaymentTransaction.objects.filter(
        invoice_id=invoice.id,
        status=PaymentTransaction.STATUS_COMPLETE
    ).first()
    context = {
        'active_page': 'billing',
        'patient': _patient_profile(request.user),
        'invoice': invoice,
        'txn': txn,
    }
    return render(request, 'patient_roshan/receipt.html', context)