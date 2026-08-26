from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from doctor_siddhartha.models import DoctorApplication
from patient_roshan.models import PatientProfile

VALID_PASSWORD = "StrongPass2026!"


class PatientRegistrationTests(TestCase):
    def test_registration_creates_user_profile_and_group(self):
        response = self.client.post("/register/", {
            "username": "newpatient",
            "email": "newpatient@example.com",
            "password": VALID_PASSWORD,
            "confirm_password": VALID_PASSWORD,
            "role": "patient",
        })
        self.assertRedirects(response, "/login/", fetch_redirect_response=False)
        user = User.objects.get(username="newpatient")
        self.assertTrue(PatientProfile.objects.filter(user=user).exists())
        self.assertTrue(user.groups.filter(name="Patient").exists())

    def test_numeric_only_password_rejected(self):
        response = self.client.post("/register/", {
            "username": "numperson",
            "email": "num@example.com",
            "password": "98765432",
            "confirm_password": "98765432",
            "role": "patient",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="numperson").exists())

    def test_common_password_rejected(self):
        response = self.client.post("/register/", {
            "username": "commonpw",
            "email": "common@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "role": "patient",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="commonpw").exists())

    def test_password_mismatch_rejected(self):
        response = self.client.post("/register/", {
            "username": "mismatch",
            "email": "mismatch@example.com",
            "password": VALID_PASSWORD,
            "confirm_password": "Different123!",
            "role": "patient",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="mismatch").exists())

    def test_duplicate_email_rejected(self):
        User.objects.create_user("existing", "taken@example.com", VALID_PASSWORD)
        response = self.client.post("/register/", {
            "username": "anotheruser",
            "email": "TAKEN@example.com",  # case-insensitive duplicate
            "password": VALID_PASSWORD,
            "confirm_password": VALID_PASSWORD,
            "role": "patient",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="anotheruser").exists())


class DoctorRegistrationTests(TestCase):
    def test_doctor_registration_creates_application_not_user(self):
        response = self.client.post("/register/", {
            "username": "futuredoc",
            "email": "futuredoc@example.com",
            "password": VALID_PASSWORD,
            "confirm_password": VALID_PASSWORD,
            "role": "doctor",
        })
        self.assertRedirects(response, "/login/")
        application = DoctorApplication.objects.get(username="futuredoc")
        self.assertEqual(application.status, DoctorApplication.STATUS_PENDING)
        self.assertFalse(User.objects.filter(username="futuredoc").exists())
        # password must be stored hashed
        self.assertNotEqual(application.password, VALID_PASSWORD)
        self.assertTrue(application.check_password(VALID_PASSWORD))

    def test_pending_application_login_shows_waiting_page(self):
        pending = DoctorApplication.objects.create(
            username="pendingdoc",
            email="pendingdoc@example.com",
        )
        pending.set_password(VALID_PASSWORD)
        pending.save()
        response = self.client.post("/login/", {
            "email": "pendingdoc@example.com",
            "password": VALID_PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth_kirtan/waiting_approval.html")
        self.assertFalse(User.objects.filter(username="pendingdoc").exists())


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("pat", "pat@example.com", VALID_PASSWORD)

    def test_valid_patient_login_redirects_to_patient_dashboard(self):
        response = self.client.post("/login/", {
            "email": "pat@example.com",
            "password": VALID_PASSWORD,
        })
        self.assertRedirects(response, "/patient/", fetch_redirect_response=False)

    def test_invalid_credentials_show_error(self):
        response = self.client.post("/login/", {
            "email": "pat@example.com",
            "password": "WrongPassword1!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password")

    def test_authenticated_patient_is_redirected_from_login(self):
        self.client.force_login(self.user)
        response = self.client.get("/login/")
        self.assertRedirects(response, "/patient/", fetch_redirect_response=False)

    def test_logout_requires_post_and_destroys_session(self):
        self.client.force_login(self.user)
        # GET is no longer allowed (logout CSRF protection).
        response = self.client.get(reverse("auth_kirtan:logout"))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse("auth_kirtan:logout"))
        self.assertRedirects(response, "/login/", fetch_redirect_response=False)
        session_key = self.client.session.session_key
        response = self.client.get("/patient/")
        if session_key:
            self.assertRedirects(response, "/login/?next=/patient/", fetch_redirect_response=False)
