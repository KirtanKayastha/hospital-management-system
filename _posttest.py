import os, django, datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital.settings")
django.setup()
from django.conf import settings

settings.ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

from django.test import Client
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from doctor_siddhartha.models import DoctorProfile
from patient_roshan.models import PatientProfile
from admin_nishan.models import Department, Appointment, DoctorAvailability
from hospital.access import ensure_patient_profile

print("=== USERS IN DB ===")
print("count:", User.objects.count())
for u in User.objects.all()[:10]:
    print("  ", u.id, u.username, "is_staff=", u.is_staff, "is_superuser=", u.is_superuser)

# Ensure a doctor + patient + department exist
dept, _ = Department.objects.get_or_create(slug="general-medicine", defaults={"name": "General Medicine"})
doc_u, _ = User.objects.get_or_create(username="dr_test", defaults={"email": "dr@t.com", "first_name": "Real", "last_name": "Doc"})
doc_u.set_password("pass1234")
doc_u.save()
DoctorProfile.objects.get_or_create(user=doc_u, defaults={"department": dept, "specialization": "Cardiology"})
pat_u, _ = User.objects.get_or_create(username="pat_test", defaults={"email": "p@t.com", "first_name": "Real", "last_name": "Pat"})
pat_u.set_password("pass1234")
pat_u.save()
ensure_patient_profile(pat_u)

c = Client()

print("\n=== BOOKING POST TEST (as patient) ===")
c.force_login(pat_u)
future = timezone.localdate() + datetime.timedelta(days=3)
payload = {
    "doctor_id": str(doc_u.id),
    "appointment_date": future.isoformat(),
    "appointment_time": "10:30",
    "reason": "Routine check",
}
before = Appointment.objects.count()
r = c.post("/patient/book/", payload)
print("status:", r.status_code, "redirect:", r.get("Location"))
after = Appointment.objects.count()
print("appointments before/after:", before, after, "-> CREATED:", after > before)
if after == before:
    print("  !! BOOKING DID NOT SAVE")
    print("  messages in response:", [str(m) for m in getattr(r, "context", {}).get("messages", [])])

print("\n=== AVAILABILITY POST TEST (as doctor) ===")
c2 = Client()
c2.force_login(doc_u)
before = DoctorAvailability.objects.count()
r2 = c2.post("/doctor/schedule/", {
    "day_of_week": "1", "start_time": "09:00", "end_time": "17:00", "is_active": "on",
})
print("status:", r2.status_code, "redirect:", r2.get("Location"))
after = DoctorAvailability.objects.count()
print("availability before/after:", before, after, "-> CREATED:", after > before)
if after == before:
    print("  !! AVAILABILITY DID NOT SAVE")
