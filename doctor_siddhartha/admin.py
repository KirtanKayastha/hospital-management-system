from django.contrib import admin

from .models import DoctorProfile, DoctorNote


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "specialization", "department", "status", "experience_years", "profile_picture_thumb")
    list_filter = ("status", "department")
    search_fields = ("user__username", "user__first_name", "user__last_name", "specialization")
    readonly_fields = ("profile_picture_thumb",)

    def profile_picture_thumb(self, obj):
        if obj.profile_picture:
            return f'<img src="{obj.profile_picture.url}" width="40" height="40" style="border-radius:50%;object-fit:cover;"/>'
        return "No photo"
    profile_picture_thumb.short_description = "Photo"
    profile_picture_thumb.allow_tags = True


@admin.register(DoctorNote)
class DoctorNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "doctor", "created_at")