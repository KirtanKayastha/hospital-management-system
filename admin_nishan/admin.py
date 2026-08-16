from django.contrib import admin
from .models import (
    Appointment,
    BillingInvoice,
    Department,
    DoctorAvailability,
    LabReport,
    MedicalRecord,
    MedicineReminder,
    Notification,
    Prescription,
    PrescriptionItem,
)


@admin.register(BillingInvoice)
class BillingInvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "patient", "appointment", "amount", "status", "issued_on", "due_on", "paid_on")
    list_filter = ("status", "issued_on")
    search_fields = ("invoice_number", "patient__username", "patient__first_name", "patient__last_name")
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("patient", "appointment", "invoice_number", "amount", "status")}),
        ("Dates", {"fields": ("issued_on", "due_on", "paid_on")}),
        ("Notes", {"fields": ("notes",)}),
        ("Metadata", {"fields": ("created_at",)}),
    )


@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "test_name", "lab_name", "ordered_date", "status", "result_date")
    list_filter = ("status", "ordered_date", "lab_name")
    search_fields = ("test_name", "lab_name", "patient__username", "patient__first_name", "patient__last_name", "doctor__username")
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("patient", "doctor", "test_name", "lab_name", "ordered_date", "result_date", "status")}),
        ("Report", {"fields": ("report_file", "summary")}),
        ("Metadata", {"fields": ("created_at",)}),
    )
