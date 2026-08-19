from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth.forms import SetPasswordForm

from .forms import PatientForm, DoctorForm

from admin_nishan.models import (
    Appointment,
    BillingInvoice,
    Department,
    InvoiceItem,
    MedicalRecord,
    Notification,
    Prescription,
)
from doctor_siddhartha.models import DoctorApplication, DoctorProfile
from hospital.access import admin_required
from hospital.notifications import notify
from patient_roshan.models import PatientProfile


def _ensure_default_department():
    department, _ = Department.objects.get_or_create(
        slug="general-medicine",
        defaults={"name": "General Medicine", "description": "General patient care and triage."},
    )
    return department


@admin_required
def admin_dashboard(request):
    today = timezone.localdate()

    weekly_counts = [
        Appointment.objects.filter(appointment_date=today - timedelta(days=i)).count()
        for i in range(6, -1, -1)
    ]
    weekly_max = max(weekly_counts) if weekly_counts else 0
    weekly_appointments = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = weekly_counts[6 - i]
        height_pct = int((count / weekly_max) * 100) if weekly_max else 0
        weekly_appointments.append(
            {"label": day.strftime("%a"), "count": count, "height_pct": max(height_pct, 4)}
        )

    recent_activity = (
        Appointment.objects.select_related("patient", "doctor", "department")
        .order_by("-created_at")[:8]
    )

    total_revenue = (
        BillingInvoice.objects.filter(status=BillingInvoice.STATUS_PAID).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    start_30 = today - timedelta(days=29)
    raw_registrations = (
        PatientProfile.objects.filter(user__date_joined__date__gte=start_30)
        .annotate(day=TruncDate("user__date_joined"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    reg_map = {item["day"]: item["count"] for item in raw_registrations}
    patient_registrations = []
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        patient_registrations.append(
            {"date": d.strftime("%b %d"), "count": reg_map.get(d, 0)}
        )

    status_qs = (
        Appointment.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )
    status_labels = {
        Appointment.STATUS_PENDING: "Pending",
        Appointment.STATUS_CONFIRMED: "Confirmed",
        Appointment.STATUS_COMPLETED: "Completed",
        Appointment.STATUS_CANCELLED: "Cancelled",
    }
    appointment_status_distribution = [
        {"status": status_labels.get(item["status"], item["status"]), "count": item["count"]}
        for item in status_qs
    ]

    doctor_workload = list(
        Appointment.objects.values("doctor__first_name", "doctor__last_name")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )
    for item in doctor_workload:
        item["name"] = f"{item.pop('doctor__first_name')} {item.pop('doctor__last_name')}".strip()

    context = {
        "active_page": "dashboard",
        "total_patients": PatientProfile.objects.count(),
        "total_doctors": DoctorProfile.objects.filter(status=DoctorProfile.STATUS_APPROVED).count(),
        "departments_count": Department.objects.count(),
        "todays_appointments": Appointment.objects.filter(appointment_date=today).count(),
        "confirmed_today": Appointment.objects.filter(
            appointment_date=today, status=Appointment.STATUS_CONFIRMED
        ).count(),
        "pending_today": Appointment.objects.filter(
            appointment_date=today, status=Appointment.STATUS_PENDING
        ).count(),
        "cancelled_today": Appointment.objects.filter(
            appointment_date=today, status=Appointment.STATUS_CANCELLED
        ).count(),
        "total_revenue": total_revenue,
        "weekly_appointments": weekly_appointments,
        "recent_activity": recent_activity,
        "patient_registrations": patient_registrations,
        "appointment_status_distribution": appointment_status_distribution,
        "doctor_workload": doctor_workload,
    }
    return render(request, "admin_dashboard.html", context)


@admin_required
def admin_manage_patients(request):
    search = request.GET.get("search", "")

    patients = PatientProfile.objects.select_related("user")

    if search:
        patients = patients.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(phone__icontains=search)
        )

    patients = patients.order_by("-user__date_joined")

    context = {
        "active_page": "patients",
        "patients": patients,
        "total_patients": patients.count(),
        "search": search,
    }

    return render(request, "admin_manage_patients.html", context)


@admin_required
def admin_manage_doctor(request):
    search = request.GET.get("search", "")

    doctors = DoctorProfile.objects.select_related(
        "user",
        "department"
    ).filter(
        status=DoctorProfile.STATUS_APPROVED
    )

    if search:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(phone__icontains=search)
        )

    doctors = doctors.order_by(
        "user__first_name",
        "user__last_name"
    )

    context = {
        "active_page": "doctor",
        "doctors": doctors,
        "total_doctors": doctors.count(),
        "search": search,
    }

    return render(request, "admin_manage_doctor.html", context)


@admin_required
def pending_doctors(request):
    # New signups live as applications (no User yet). Legacy pending profiles
    # already have a User, so both lists are shown.
    applications = (
        DoctorApplication.objects.select_related("department")
        .filter(status=DoctorApplication.STATUS_PENDING)
        .order_by("created_at")
    )
    legacy_profiles = (
        DoctorProfile.objects.select_related("user", "department")
        .filter(status=DoctorProfile.STATUS_PENDING)
        .order_by("user__date_joined")
    )
    context = {
        "active_page": "pending_doctors",
        "applications": applications,
        "pending_doctors": legacy_profiles,
        "total_pending": applications.count() + legacy_profiles.count(),
    }
    return render(request, "admin_nishan/pending_doctors.html", context)


@admin_required
def approve_application(request, application_id):
    application = get_object_or_404(DoctorApplication, pk=application_id)

    if application.status == DoctorApplication.STATUS_APPROVED:
        messages.info(request, f"{application.display_name} is already approved.")
        return redirect("admin_nishan:pending_doctors")

    if User.objects.filter(username__iexact=application.username).exists() or \
            User.objects.filter(email__iexact=application.email).exists():
        messages.error(
            request,
            f"Cannot approve {application.username}: that username or email is already taken."
        )
        return redirect("admin_nishan:pending_doctors")

    try:
        with transaction.atomic():
            user = User(
                username=application.username,
                email=application.email,
                first_name=application.first_name,
                last_name=application.last_name,
            )
            # Reuse the hash captured at registration; the password is never known here.
            user.password = application.password
            user.save()

            group, _ = Group.objects.get_or_create(name="Doctor")
            user.groups.add(group)

            DoctorProfile.objects.create(
                user=user,
                department=application.department or _ensure_default_department(),
                specialization=application.specialization or "General Medicine",
                qualification=application.qualification,
                experience_years=application.experience_years,
                license_number=application.license_number,
                phone=application.phone,
                consultation_fee=0,
                bio="",
                status=DoctorProfile.STATUS_APPROVED,
            )

            application.status = DoctorApplication.STATUS_APPROVED
            application.reviewed_at = timezone.now()
            application.save(update_fields=["status", "reviewed_at"])
    except IntegrityError as exc:
        messages.error(request, f"Could not approve {application.username}: {exc}")
        return redirect("admin_nishan:pending_doctors")

    notify(
        user,
        "Account approved",
        "Your doctor account has been approved. You can now log in with the "
        "credentials you registered with.",
        category=Notification.CATEGORY_GENERAL,
        action_url="/login/",
    )

    messages.success(request, f"Dr. {application.display_name} approved and account created.")
    return redirect("admin_nishan:pending_doctors")


@admin_required
def reject_application(request, application_id):
    application = get_object_or_404(DoctorApplication, pk=application_id)
    application.status = DoctorApplication.STATUS_REJECTED
    application.reviewed_at = timezone.now()
    application.save(update_fields=["status", "reviewed_at"])
    messages.warning(request, f"Application from {application.display_name} rejected.")
    return redirect("admin_nishan:pending_doctors")


@admin_required
def approve_doctor(request, doctor_id):
    profile = get_object_or_404(DoctorProfile, pk=doctor_id)
    profile.status = DoctorProfile.STATUS_APPROVED
    profile.save(update_fields=["status"])
    messages.success(request, f"Dr. {profile.display_name} has been approved.")
    return redirect("admin_nishan:pending_doctors")


@admin_required
def reject_doctor(request, doctor_id):
    profile = get_object_or_404(DoctorProfile, pk=doctor_id)
    profile.status = DoctorProfile.STATUS_REJECTED
    profile.save(update_fields=["status"])
    messages.warning(request, f"Dr. {profile.display_name} has been rejected.")
    return redirect("admin_nishan:pending_doctors")


@admin_required
def admin_appointments(request):
    appointments = (
        Appointment.objects.select_related("patient", "doctor", "department").order_by(
            "-appointment_date", "-appointment_time"
        )
    )
    context = {
        "active_page": "appointments",
        "appointments": appointments,
        "total_appointments": appointments.count(),
    }
    return render(request, "admin_appointments.html", context)


@admin_required
def admin_reports(request):
    today = timezone.localdate()

    # Appointment Trends (Last 8 Weeks)
    week_start = today - timedelta(days=today.weekday())

    raw_trends = []

    for i in range(7, -1, -1):
        ws = week_start - timedelta(weeks=i)
        we = ws + timedelta(days=6)

        count = Appointment.objects.filter(
            appointment_date__range=(ws, we)
        ).count()

        raw_trends.append(count)

    max_trend = max(raw_trends) if raw_trends else 0

    appointment_trends = []

    for index, count in enumerate(raw_trends):
        height_pct = int((count / max_trend) * 100) if max_trend else 4

        appointment_trends.append({
            "count": count,
            "height_pct": max(height_pct, 4),
            "label": f"W{index + 1}",
        })

    # Department Distribution
    department_distribution = (
        Department.objects
        .annotate(appt_count=Count("appointments"))
        .order_by("-appt_count")
    )

    total_dept = (
        sum(d.appt_count for d in department_distribution)
        or 1
    )

    # Revenue from BillingInvoice model
    total_revenue = (
        BillingInvoice.objects.filter(
            status=BillingInvoice.STATUS_PAID
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    print("Revenue:", total_revenue)

    context = {
        "active_page": "reports",

        "total_patients": PatientProfile.objects.count(),
        "total_doctors": DoctorProfile.objects.count(),
        "total_appointments": Appointment.objects.count(),
        "total_records": MedicalRecord.objects.count(),
        "total_prescriptions": Prescription.objects.count(),

        "total_revenue": total_revenue,

        "appointment_trends": appointment_trends,
        "max_trend": max_trend,

        "department_distribution": department_distribution,
        "total_dept": total_dept,
    }

    return render(
        request,
        "admin_reports.html",
        context,
    )

@admin_required
def edit_patient(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)

    if request.method == "POST":
        form = PatientForm(request.POST, request.FILES, instance=patient)

        if form.is_valid():
            form.save()
            messages.success(request, "Patient updated successfully.")
            return redirect("admin_nishan:admin_manage_patients")
    else:
        form = PatientForm(instance=patient)

    context = {
        "active_page": "patients",
        "form": form,
        "patient": patient,
    }

    return render(request, "admin_nishan/edit_patient.html", context)

@admin_required
def edit_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id)

    if request.method == "POST":
        form = DoctorForm(request.POST, instance=doctor)

        if form.is_valid():
            form.save()
            messages.success(request, "Doctor updated successfully.")
            return redirect("admin_nishan:admin_manage_doctor")
    else:
        form = DoctorForm(instance=doctor)

    context = {
        "active_page": "doctor",
        "form": form,
        "doctor": doctor,
    }

    return render(request, "admin_nishan/edit_doctor.html", context)

@admin_required
def change_doctor_password(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
    user = doctor.user

    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Doctor password changed successfully.")
            return redirect("admin_nishan:admin_manage_doctor")
    else:
        form = SetPasswordForm(user)

    return render(
        request,
        "admin_nishan/change_password.html",
        {
            "form": form,
            "title": f"Change Password - Dr. {doctor.display_name}",
        },
    )


@admin_required
def enable_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id)

    doctor.user.is_active = True
    doctor.user.save()

    messages.success(request, "Doctor login enabled successfully.")
    return redirect("admin_nishan:admin_manage_doctor")


@admin_required
def disable_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id)

    doctor.user.is_active = False
    doctor.user.save()

    messages.success(request, "Doctor login disabled successfully.")
    return redirect("admin_nishan:admin_manage_doctor")


@admin_required
def delete_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id)

    if doctor.user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("admin_nishan:admin_manage_doctor")

    doctor.user.delete()

    messages.success(request, "Doctor deleted successfully.")
    return redirect("admin_nishan:admin_manage_doctor")


@admin_required
def change_patient_password(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)
    user = patient.user

    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Patient password changed successfully.")
            return redirect("admin_nishan:admin_manage_patients")
    else:
        form = SetPasswordForm(user)

    return render(
        request,
        "admin_nishan/change_password.html",
        {
            "form": form,
            "title": f"Change Password - {user.get_full_name() or user.username}",
        },
    )


@admin_required
def enable_patient(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)

    patient.user.is_active = True
    patient.user.save()

    messages.success(request, "Patient login enabled.")
    return redirect("admin_nishan:admin_manage_patients")


@admin_required
def disable_patient(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)

    if patient.user == request.user:
        messages.error(request, "You cannot disable your own account.")
        return redirect("admin_nishan:admin_manage_patients")

    patient.user.is_active = False
    patient.user.save()

    messages.success(request, "Patient login disabled.")
    return redirect("admin_nishan:admin_manage_patients")


@admin_required
def delete_patient(request, patient_id):
    patient = get_object_or_404(PatientProfile, pk=patient_id)

    if patient.user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("admin_nishan:admin_manage_patients")

    patient.user.delete()

    messages.success(request, "Patient deleted successfully.")
    return redirect("admin_nishan:admin_manage_patients")



# def admin_billing(request):

#     invoices = BillingInvoice.objects.all().order_by("-id")

#     context = {
#         "active_page": "billing",
#         "invoices": invoices,
#     }

#     return render(request, "admin_nishan/admin_billing.html", context)
@admin_required
def admin_billing(request):

    status_filter = request.GET.get("status")
    search = (request.GET.get("search", "") or "").strip()

    invoices = BillingInvoice.objects.select_related("patient").all().order_by("-created_at")

    if status_filter:
        invoices = invoices.filter(status=status_filter)

    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search) |
            Q(patient__username__icontains=search)
        )

    context = {
        "active_page": "billing",
        "invoices": invoices,
        "status_filter": status_filter,
        "search": search,
    }

    return render(
        request,
        "admin_nishan/admin_billing.html",
        context
    )




def _next_invoice_number(issued_on):
    """Collision-proof: derive the suffix from the highest existing number for
    that day, not from count(), which repeats after a deletion."""
    prefix = f"INV-{issued_on.strftime('%Y%m%d')}-"
    existing = BillingInvoice.objects.filter(
        invoice_number__startswith=prefix
    ).values_list("invoice_number", flat=True)
    highest = 0
    for number in existing:
        suffix = number[len(prefix):]
        if suffix.isdigit():
            highest = max(highest, int(suffix))
    return f"{prefix}{highest + 1:04d}"


def _parse_items(request):
    """Returns (items, errors). Values are coerced to int/Decimal here."""
    descriptions = request.POST.getlist("description[]")
    quantities = request.POST.getlist("quantity[]")
    unit_prices = request.POST.getlist("unit_price[]")

    items, errors = [], []
    for index, desc in enumerate(descriptions):
        desc = (desc or "").strip()
        raw_qty = quantities[index] if index < len(quantities) else ""
        raw_price = unit_prices[index] if index < len(unit_prices) else ""

        if not desc and not (raw_qty or "").strip() and not (raw_price or "").strip():
            continue  # entirely blank row, ignore
        if not desc:
            errors.append(f"Row {index + 1}: description is required.")
            continue

        try:
            qty = int(raw_qty or 1)
        except (TypeError, ValueError):
            errors.append(f"Row {index + 1}: quantity must be a whole number.")
            continue
        if qty <= 0:
            errors.append(f"Row {index + 1}: quantity must be greater than 0.")
            continue

        try:
            price = Decimal(str(raw_price or "0"))
        except (InvalidOperation, TypeError, ValueError):
            errors.append(f"Row {index + 1}: unit price must be a number.")
            continue
        if price < 0:
            errors.append(f"Row {index + 1}: unit price cannot be negative.")
            continue

        items.append({"description": desc, "quantity": qty, "unit_price": price})

    return items, errors


def _parse_tax_rate(raw, fallback=Decimal("0.13")):
    """Form sends a percentage (13); the model stores a fraction (0.13)."""
    if raw in (None, ""):
        return fallback
    try:
        return (Decimal(str(raw)) / Decimal("100")).quantize(Decimal("0.0001"))
    except (InvalidOperation, TypeError, ValueError):
        return fallback


@admin_required
def create_invoice(request):
    today = timezone.localdate()
    invoice_number = _next_invoice_number(today)

    if request.method == "POST":
        patient_id = (request.POST.get("patient") or "").strip()
        patient_profile = (
            PatientProfile.objects.filter(id=patient_id).first()
            if patient_id.isdigit()
            else None
        )
        items, errors = _parse_items(request)

        if not patient_profile:
            errors.insert(0, "Select a valid patient.")
        if not items:
            errors.insert(0, "Add at least one line item before saving.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(
                request,
                "admin_nishan/admin_create_invoice.html",
                {
                    "active_page": "billing",
                    "patients": PatientProfile.objects.all(),
                    "invoice_number": invoice_number,
                    "edit_mode": False,
                    "default_tax_rate": request.POST.get("tax_rate") or 13,
                    "today": today,
                    "selected_patient_id": int(patient_id) if patient_id.isdigit() else None,
                    "posted_items": items,
                    "posted_notes": request.POST.get("notes", ""),
                },
            )

        try:
            with transaction.atomic():
                invoice = BillingInvoice.objects.create(
                    patient=patient_profile.user,
                    invoice_number=_next_invoice_number(today),
                    amount=0,
                    subtotal=0,
                    tax_rate=_parse_tax_rate(request.POST.get("tax_rate")),
                    tax_amount=0,
                    grand_total=0,
                    status=request.POST.get("status") or BillingInvoice.STATUS_UNPAID,
                    issued_on=today,
                    due_on=request.POST.get("due_on") or None,
                    notes=request.POST.get("notes", ""),
                )
                for item in items:
                    InvoiceItem.objects.create(invoice=invoice, **item)
                invoice.recalculate_totals()
        except (IntegrityError, InvalidOperation, ValidationError) as exc:
            messages.error(request, f"Could not create the invoice: {exc}")
            return redirect("admin_nishan:create_invoice")

        invoice.refresh_from_db()

        notify(
            patient_profile.user,
            "New Invoice Generated",
            f"Invoice {invoice.invoice_number} for Rs. {invoice.grand_total:,.2f} has been created. "
            f"Due date: {invoice.due_on.strftime('%b %d, %Y') if invoice.due_on else 'N/A'}.",
            category=Notification.CATEGORY_BILLING,
            action_url="/patient/invoices/",
        )

        messages.success(request, f"Invoice {invoice.invoice_number} created successfully.")
        return redirect("admin_nishan:admin_billing")

    context = {
        "active_page": "billing",
        "patients": PatientProfile.objects.all(),
        "invoice_number": invoice_number,
        "edit_mode": False,
        "default_tax_rate": 13,
        "today": today,
    }

    return render(
        request,
        "admin_nishan/admin_create_invoice.html",
        context,
    )


@admin_required
def edit_invoice(request, invoice_id):
    invoice = get_object_or_404(BillingInvoice, id=invoice_id)

    if request.method == "POST":
        items, errors = _parse_items(request)
        if not items:
            errors.insert(0, "An invoice must have at least one line item.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect("admin_nishan:edit_invoice", invoice_id=invoice.id)

        try:
            with transaction.atomic():
                invoice.status = request.POST.get("status") or invoice.status
                invoice.notes = request.POST.get("notes", invoice.notes)
                invoice.due_on = request.POST.get("due_on") or invoice.due_on
                invoice.tax_rate = _parse_tax_rate(
                    request.POST.get("tax_rate"), fallback=invoice.tax_rate
                )

                if invoice.status == BillingInvoice.STATUS_PAID and not invoice.paid_on:
                    invoice.paid_on = timezone.localdate()

                invoice.save()
                invoice.items.all().delete()
                for item in items:
                    InvoiceItem.objects.create(invoice=invoice, **item)
                invoice.recalculate_totals()
        except (IntegrityError, InvalidOperation, ValidationError) as exc:
            messages.error(request, f"Could not update the invoice: {exc}")
            return redirect("admin_nishan:edit_invoice", invoice_id=invoice.id)

        invoice.refresh_from_db()
        messages.success(request, f"Invoice {invoice.invoice_number} updated successfully.")
        return redirect("admin_nishan:admin_billing")

    context = {
        "invoice": invoice,
        "patients": PatientProfile.objects.all(),
        "invoice_number": invoice.invoice_number,
        "edit_mode": True,
        "selected_patient_id": invoice.patient.patient_profile.id if hasattr(invoice.patient, "patient_profile") else None,
        "items": invoice.items.all(),
        "default_tax_rate": invoice.tax_rate_percent,
    }

    return render(
        request,
        "admin_nishan/admin_create_invoice.html",
        context,
    )


@admin_required
def mark_paid(request, invoice_id):
    invoice = get_object_or_404(BillingInvoice, id=invoice_id)
    invoice.status = BillingInvoice.STATUS_PAID
    invoice.paid_on = timezone.localdate()
    invoice.save(update_fields=["status", "paid_on"])
    messages.success(request, f"Invoice {invoice.invoice_number} marked as paid.")
    return redirect("admin_nishan:admin_billing")


@admin_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(BillingInvoice.objects.select_related("patient"), id=invoice_id)
    context = {
        "active_page": "billing",
        "invoice": invoice,
    }
    return render(request, "admin_nishan/admin_invoice_detail.html", context)


@admin_required
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(BillingInvoice, id=invoice_id)
    invoice.delete()

    return redirect("admin_nishan:admin_billing")

@admin_required
def print_invoice(request, invoice_id):
    invoice = get_object_or_404(BillingInvoice, id=invoice_id)

    return render(
        request,
        "admin_nishan/print_invoice.html",
        {"invoice": invoice}
    )