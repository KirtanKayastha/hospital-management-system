from django.shortcuts import redirect, render

from hospital.access import get_user_role


def home_view(request):
    if request.user.is_authenticated:
        role = get_user_role(request.user)
        if role == 'admin':
            return redirect('/admin-panel/')
        elif role == 'doctor':
            return redirect('/doctor/dashboard/')
        elif role == 'patient':
            return redirect('/patient/')
        return redirect('/patient/')
    return render(request, 'home.html')
