from django.contrib import admin

from .models import DoctorProfile, DoctorNote


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "specialization", "department", "status", "experience_years")
    list_filter = ("status", "department")
    search_fields = ("user__username", "user__first_name", "user__last_name", "specialization")


@admin.register(DoctorNote)
class DoctorNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "doctor", "created_at")