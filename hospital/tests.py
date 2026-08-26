from django.contrib.auth.models import User
from django.test import Client, TestCase

from admin_nishan.models import Department
from doctor_siddhartha.models import DoctorProfile


class AccessControlTests(TestCase):
    """Role isolation: every dashboard is invisible to the wrong role."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("rootadmin", "root@example.com", "RootAdmin2026!")
        cls.doctor_user = User.objects.create_user("doc", "doc@example.com", "DocPass2026!")
        department, _ = Department.objects.get_or_create(
            slug="general-medicine",
            defaults={"name": "General Medicine"},
        )
        DoctorProfile.objects.create(
            user=cls.doctor_user,
            department=department,
            specialization="General Medicine",
            status=DoctorProfile.STATUS_APPROVED,
        )

    def test_unauthenticated_users_are_redirected_to_login(self):
        for url in ["/patient/", "/doctor/dashboard/", "/admin-panel/"]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/login/", response["Location"])

    def test_patient_cannot_access_doctor_or_admin_pages(self):
        from patient_roshan.models import PatientProfile
        patient = User.objects.create_user("plainpat", "plainpat@example.com", "PatPass2026!")
        PatientProfile.objects.get_or_create(user=patient)
        self.client.force_login(patient)
        for url in ["/doctor/dashboard/", "/doctor/schedule/", "/admin-panel/", "/admin-panel/patients/"]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403)

    def test_doctor_cannot_access_patient_or_admin_pages(self):
        self.client.force_login(self.doctor_user)
        for url in ["/patient/", "/patient/appointments/", "/admin-panel/", "/admin-panel/billing/"]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403)

    def test_admin_can_access_all_dashboards(self):
        self.client.force_login(self.admin)
        for url in ["/admin-panel/", "/admin-panel/patients/", "/admin-panel/pending-doctors/",
                    "/admin-panel/appointments/", "/admin-panel/reports/", "/admin-panel/billing/"]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)


class PublicPagesTests(TestCase):
    def test_public_pages_render(self):
        for url in ["/", "/login/", "/register/", "/faq/", "/privacy-policy/", "/terms/", "/support/", "/about/"]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_csrf_token_present_on_login_and_register(self):
        for url in ["/login/", "/register/"]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "csrfmiddlewaretoken")

    def test_post_without_csrf_token_is_rejected(self):
        # The stock test client bypasses CSRF; enforce it explicitly here.
        strict_client = Client(enforce_csrf_checks=True)
        response = strict_client.post("/login/", {"email": "x@x.com", "password": "whatever1"})
        self.assertEqual(response.status_code, 403)

    def test_debug_endpoint_removed(self):
        response = self.client.get("/db-check/")
        self.assertEqual(response.status_code, 404)
