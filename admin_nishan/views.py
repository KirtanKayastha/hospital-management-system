from django.shortcuts import render

def admin_dashboard(request):
    return render(request, "admin_dashboard.html")

def admin_accounts(request):
    return render(request, "admin_accounts.html")

def admin_appointments(request):
    return render(request, "admin_appointments.html")

def admin_manage_doctor(request):
    return render(request, "admin_manage_doctor.html")

def admin_manage_patients(request):
    return render(request, "admin_manage_patients.html")

def admin_reports(request):
    return render(request, "admin_reports.html")
