from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import PatientForm, DoctorForm
from django.contrib.auth.forms import SetPasswordForm
from django.db.models import Q
from patient_roshan.models import PatientProfile
from .models import Invoice
from django.shortcuts import get_object_or_404, redirect, render
from .models import Invoice



from admin_nishan.models import (
    Appointment,
    BillingInvoice,
    Department,
    MedicalRecord,
    Prescription,
)
from doctor_siddhartha.models import DoctorProfile
from hospital.access import admin_required
from patient_roshan.models import PatientProfile


@admin_required
def delete_account(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if target.id == request.user.id:
        messages.error(request, "You cannot delete your own account.")
        return redirect("admin_nishan:admin_accounts")
    if not request.user.is_superuser:
        messages.error(request, "Only superusers can delete accounts.")
        return redirect("admin_nishan:admin_accounts")
    username = target.get_full_name() or target.username
    target.delete()
    messages.success(request, f"Account '{username}' has been deleted.")
    return redirect("admin_nishan:admin_accounts")

from admin_nishan.models import (
    Appointment,
    BillingInvoice,
    Department,
    MedicalRecord,
    Prescription,
)
from doctor_siddhartha.models import DoctorProfile
from hospital.access import admin_required
from patient_roshan.models import PatientProfile


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
    pending_doctors = (
        DoctorProfile.objects.select_related("user", "department")
        .filter(status=DoctorProfile.STATUS_PENDING)
        .order_by("user__date_joined")
    )
    context = {
        "active_page": "pending_doctors",
        "pending_doctors": pending_doctors,
        "total_pending": pending_doctors.count(),
    }
    return render(request, "admin_nishan/pending_doctors.html", context)


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


from django.db.models import Q
from django.contrib.auth.models import User
from patient_roshan.models import PatientProfile
from doctor_siddhartha.models import DoctorProfile


@admin_required
def admin_accounts(request):

    approved_doctor_ids = DoctorProfile.objects.filter(
        status=DoctorProfile.STATUS_APPROVED
    ).values_list("user_id", flat=True)

    patient_ids = PatientProfile.objects.values_list(
        "user_id",
        flat=True
    )

    accounts = User.objects.filter(
        is_staff=False
    ).filter(
        Q(id__in=patient_ids) |
        Q(id__in=approved_doctor_ids)
    ).distinct().order_by("-date_joined")

    context = {
        "active_page": "accounts",
        "accounts": accounts,
        "total_accounts": accounts.count(),
        "total_patients": PatientProfile.objects.count(),
        "total_doctors": DoctorProfile.objects.filter(
            status=DoctorProfile.STATUS_APPROVED
        ).count(),
    }

    return render(request, "admin_accounts.html", context)


@admin_required
def admin_reports(request):
    today = timezone.localdate()

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
        appointment_trends.append(
            {"count": count, "height_pct": max(height_pct, 4), "label": f"W{index + 1}"}
        )

    department_distribution = (
        Department.objects.annotate(appt_count=Count("appointments")).order_by(
            "-appt_count"
        )
    )
    total_dept = (
        sum(d.appt_count for d in department_distribution) or 1
    )

    total_revenue = (
        BillingInvoice.objects.filter(status=BillingInvoice.STATUS_PAID).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

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
    return render(request, "admin_reports.html", context)

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

#     invoices = Invoice.objects.all().order_by("-id")

#     context = {
#         "active_page": "billing",
#         "invoices": invoices,
#     }

#     return render(request, "admin_nishan/admin_billing.html", context)
@admin_required
def admin_billing(request):

    status_filter = request.GET.get("status")

    invoices = Invoice.objects.all().order_by("-created_at")

    if status_filter:
        invoices = invoices.filter(status=status_filter)

    context = {
        "active_page": "billing",
        "invoices": invoices,
        "status_filter": status_filter,
    }

    return render(
        request,
        "admin_nishan/admin_billing.html",
        context
    )




from django.shortcuts import render, redirect
from patient_roshan.models import PatientProfile
from .models import Invoice


@admin_required
def create_invoice(request):

    last_invoice = Invoice.objects.order_by('-id').first()

    if last_invoice:
        invoice_number = f"INV-{last_invoice.id + 1:04d}"
    else:
        invoice_number = "INV-0001"

    if request.method == "POST":

        patient = PatientProfile.objects.get(
            id=request.POST.get("patient")
        )

        amount = request.POST.get("amount")
        status = request.POST.get("status")

        payment_method = request.POST.get("payment_method")
        online_provider = request.POST.get("online_provider")

        if payment_method == "Online Banking":
            payment_method = online_provider

        Invoice.objects.create(
            patient=patient,
            invoice_number=invoice_number,
            amount=amount,
            status=status,
            payment_method=payment_method,
        )

        return redirect("admin_nishan:admin_billing")

    context = {
        "patients": PatientProfile.objects.all(),
        "invoice_number": invoice_number,
    }

    return render(
        request,
        "admin_nishan/admin_create_invoice.html",
        context,
    )


from django.shortcuts import get_object_or_404, redirect, render

@admin_required
def edit_invoice(request, invoice_id):

    invoice = get_object_or_404(Invoice, id=invoice_id)

    if request.method == "POST":
        invoice.amount = request.POST.get("amount")
        invoice.status = request.POST.get("status")
        invoice.payment_method = request.POST.get("payment_method")
        invoice.save()

        return redirect("admin_nishan:admin_billing")

    context = {
        "invoice": invoice,
        "patients": PatientProfile.objects.all(),
        "invoice_number": invoice.invoice_number,
        "edit_mode": True,
    }

    return render(
        request,
        "admin_nishan/admin_create_invoice.html",
        context,
    )

@admin_required
def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice.delete()

    return redirect("admin_nishan:admin_billing")

@admin_required
def print_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    return render(
        request,
        "admin_nishan/print_invoice.html",
        {"invoice": invoice}
    )