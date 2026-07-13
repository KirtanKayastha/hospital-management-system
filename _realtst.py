import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital.settings")
django.setup()
from django.conf import settings

settings.ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

from django.test import Client
from django.contrib.auth.models import User

def hit(user, urls):
    c = Client()
    if user:
        c.force_login(user)
    for u in urls:
        try:
            r = c.get(u)
            flag = "" if r.status_code == 200 else "  <-- NOT 200"
            print(f"  {r.status_code}  {u}{flag}")
        except Exception as e:
            print(f"  ERROR {u}: {type(e).__name__}: {str(e)[:200]}")

admin = User.objects.get(id=1)
doctor1 = User.objects.filter(username="doctor1").first()
patient1 = User.objects.filter(username="patient1").first()

print("ADMIN pages:")
hit(admin, ["/admin-panel/", "/admin-panel/patients/", "/admin-panel/doctor/",
            "/admin-panel/appointments/", "/admin-panel/accounts/", "/admin-panel/reports/"])
print("DOCTOR1 pages:")
hit(doctor1, ["/doctor/dashboard/", "/doctor/schedule/", "/doctor/patients/", "/doctor/prescriptions/"])
print("PATIENT1 pages:")
hit(patient1, ["/patient/", "/patient/book/", "/patient/appointments/", "/patient/records/", "/patient/profile/"])
print("UNAUTH (should redirect to login):")
hit(None, ["/patient/", "/doctor/dashboard/", "/admin-panel/"])
