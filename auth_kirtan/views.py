from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Role-based redirect
                if user.is_superuser:
                    return redirect('/admin-panel/')
                elif hasattr(user, 'patient_profile'):
                    return redirect('/patient/')
                elif hasattr(user, 'doctor_profile'):
                    return redirect('/doctor/dashboard/')
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
        
        # Create role-specific profile
        if role == 'patient':
            from patient_roshan.models import PatientProfile
            PatientProfile.objects.create(user=user)
        elif role == 'doctor':
            from doctor_siddhartha.models import DoctorProfile
            DoctorProfile.objects.create(user=user)
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('/login/')
    
    return render(request, 'auth_kirtan/register.html')

def logout_view(request):
    logout(request)
    return redirect('/login/')