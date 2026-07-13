from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


ROLE_ADMIN = "admin"
ROLE_DOCTOR = "doctor"
ROLE_PATIENT = "patient"


def get_user_role(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser or user.is_staff:
        return ROLE_ADMIN
    if hasattr(user, "doctor_profile"):
        return ROLE_DOCTOR
    if hasattr(user, "patient_profile"):
        return ROLE_PATIENT
    group_names = set(user.groups.values_list("name", flat=True))
    if {"Doctor", "Doctors"} & group_names:
        return ROLE_DOCTOR
    if {"Patient", "Patients"} & group_names:
        return ROLE_PATIENT
    return ROLE_PATIENT


def role_required(*allowed_roles):
    allowed = set(allowed_roles)

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            role = get_user_role(request.user)
            if request.user.is_superuser or role in allowed:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied

        return wrapped

    return decorator


def patient_required(view_func):
    return role_required(ROLE_PATIENT)(view_func)


def doctor_required(view_func):
    return role_required(ROLE_DOCTOR)(view_func)


def admin_required(view_func):
    return role_required(ROLE_ADMIN)(view_func)


def ensure_patient_profile(user):
    from patient_roshan.models import PatientProfile

    profile, _ = PatientProfile.objects.get_or_create(user=user)
    return profile
