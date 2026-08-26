from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from doctor_siddhartha.models import DoctorApplication
from hospital.access import ensure_patient_profile, get_user_role


def _ensure_default_department():
    from admin_nishan.models import Department

    department, _ = Department.objects.get_or_create(
        slug="general-medicine",
        defaults={"name": "General Medicine", "description": "General patient care and triage."},
    )
    return department


def _ensure_doctor_profile(user):
    from doctor_siddhartha.models import DoctorProfile

    department = _ensure_default_department()
    profile, created = DoctorProfile.objects.get_or_create(
        user=user,
        defaults={
            "department": department,
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
        profile.department = department
        profile.save(update_fields=["specialization", "department"])
    return profile


def _role_home(user):
    """Where an authenticated user belongs. Returns None when the doctor is not
    yet cleared, so callers render the waiting page instead of redirecting into
    a guard that would bounce straight back here."""
    from doctor_siddhartha.models import DoctorProfile

    role = get_user_role(user)
    if role == 'admin':
        return '/admin-panel/'
    if role == 'doctor':
        profile = getattr(user, 'doctor_profile', None)
        if profile is not None and profile.status in (
            DoctorProfile.STATUS_PENDING,
            DoctorProfile.STATUS_REJECTED,
        ):
            return None
        return '/doctor/dashboard/'
    if role == 'patient':
        return '/patient/'
    return '/'


def login_view(request):
    if request.user.is_authenticated:
        destination = _role_home(request.user)
        if destination is None:
            # Pending/rejected doctor: never redirect to the dashboard, whose
            # guard redirects back to /login/ -> infinite loop.
            return render(request, 'auth_kirtan/waiting_approval.html')
        return redirect(destination)

    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''

        # A doctor awaiting review has no User row yet, so authenticate() would
        # just say "invalid credentials". Check applications first.
        application = DoctorApplication.objects.filter(email__iexact=email).first()
        if application and application.check_password(password):
            if application.status == DoctorApplication.STATUS_PENDING:
                return render(request, 'auth_kirtan/waiting_approval.html', {
                    'application': application,
                })
            if application.status == DoctorApplication.STATUS_REJECTED:
                return render(request, 'auth_kirtan/waiting_approval.html', {
                    'application': application,
                    'rejected': True,
                })

        user_obj = User.objects.filter(email__iexact=email).first()
        if user_obj is not None:
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)

                role = get_user_role(user)
                if role == 'patient':
                    ensure_patient_profile(user)

                destination = _role_home(user)
                if destination is None:
                    return render(request, 'auth_kirtan/waiting_approval.html')
                return redirect(destination)

        messages.error(request, 'Invalid email or password')

    return render(request, 'auth_kirtan/login.html')


def register_view(request):
    if request.user.is_authenticated:
        destination = _role_home(request.user)
        if destination is None:
            return render(request, 'auth_kirtan/waiting_approval.html')
        return redirect(destination)

    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''
        confirm_password = request.POST.get('confirm_password') or ''
        role = request.POST.get('role') or 'patient'

        def fail(message):
            messages.error(request, message)
            return render(request, 'auth_kirtan/register.html')

        if not username or not email or not password:
            return fail('Username, email and password are required.')
        if password != confirm_password:
            return fail('Passwords do not match')

        # create_user() does not run AUTH_PASSWORD_VALIDATORS, so enforce them here.
        # An unsaved User lets UserAttributeSimilarityValidator compare against
        # the username/email the person just typed.
        try:
            validate_password(password, User(username=username, email=email))
        except DjangoValidationError as exc:
            return fail(' '.join(exc.messages))

        if User.objects.filter(username__iexact=username).exists() or \
                DoctorApplication.objects.filter(username__iexact=username).exists():
            return fail('Username already exists')
        if User.objects.filter(email__iexact=email).exists() or \
                DoctorApplication.objects.filter(email__iexact=email).exists():
            return fail('Email already registered')

        if role == 'doctor':
            # No User account until an admin approves.
            application = DoctorApplication(
                username=username,
                email=email,
                department=_ensure_default_department(),
                specialization='General Medicine',
                status=DoctorApplication.STATUS_PENDING,
            )
            application.set_password(password)
            application.save()
            messages.success(
                request,
                'Application submitted. An administrator must approve your account '
                'before you can log in.'
            )
            return redirect('/login/')

        user = User.objects.create_user(username=username, email=email, password=password)
        role_group, _ = Group.objects.get_or_create(name=role.title())
        user.groups.add(role_group)

        if role == 'patient':
            ensure_patient_profile(user)

        messages.success(request, 'Account created successfully! Please login.')
        return redirect('/login/')

    return render(request, 'auth_kirtan/register.html')


@require_POST
def logout_view(request):
    storage = get_messages(request)
    list(storage)
    logout(request)
    return redirect('/login/')