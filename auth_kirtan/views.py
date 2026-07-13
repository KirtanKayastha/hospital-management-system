from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect, render

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


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            
            if user is not None:
                login(request, user)

                role = get_user_role(user)
                if role == 'patient':
                    ensure_patient_profile(user)
                elif role == 'doctor':
                    _ensure_doctor_profile(user)
                
                # Role-based redirect
                if role == 'admin':
                    return redirect('/admin-panel/')
                elif role == 'doctor':
                    return redirect('/doctor/dashboard/')
                elif role == 'patient':
                    return redirect('/patient/')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid email or password')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'auth_kirtan/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'auth_kirtan/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'auth_kirtan/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'auth_kirtan/register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        role_group, _ = Group.objects.get_or_create(name=role.title())
        user.groups.add(role_group)

        # Create role-specific profile
        if role == 'patient':
            ensure_patient_profile(user)
        elif role == 'doctor':
            _ensure_doctor_profile(user)

        messages.success(request, 'Account created successfully! Please login.')
        return redirect('/login/')

    return render(request, 'auth_kirtan/register.html')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email and User.objects.filter(email=email).exists():
            messages.success(request, 'If the email exists, password reset instructions have been prepared.')
        else:
            messages.success(request, 'If the email exists, password reset instructions have been prepared.')
    return render(request, 'auth_kirtan/forgot_password.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')