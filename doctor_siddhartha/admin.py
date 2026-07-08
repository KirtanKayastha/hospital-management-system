from django.contrib import admin
from .models import (
    DoctorProfile, Patient, Vitals, Appointment,
    Availability, Prescription, PrescriptionItem,
)


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date_issued')
    list_filter = ('doctor', 'date_issued')
    search_fields = ('patient__full_name', 'diagnosis')
    inlines = [PrescriptionItemInline]


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'full_name', 'age', 'gender', 'contact_number', 'assigned_doctor')
    search_fields = ('full_name', 'patient_id', 'contact_number')
    list_filter = ('gender', 'blood_group', 'assigned_doctor')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'start_time', 'appointment_type', 'status')
    list_filter = ('status', 'appointment_type', 'date', 'doctor')
    search_fields = ('patient__full_name',)
    date_hierarchy = 'date'


admin.site.register(DoctorProfile)
admin.site.register(Vitals)
admin.site.register(Availability)