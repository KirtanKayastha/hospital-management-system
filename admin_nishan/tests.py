from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from admin_nishan.models import (
    Appointment,
    BillingInvoice,
    Department,
    InvoiceItem,
)
from doctor_siddhartha.models import DoctorApplication, DoctorProfile
from hospital.access import ensure_patient_profile


class AdminActionTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("rootadmin", "root@example.com", "RootAdmin2026!")
        cls.department = Department.objects.create(slug="general-qa", name="General QA")


class DoctorApprovalTests(AdminActionTestBase):
    def test_approving_application_creates_user_and_profile(self):
        application = DoctorApplication.objects.create(
            username="applicant",
            email="applicant@example.com",
        )
        application.set_password("ApplicantPass1!")
        application.save()

        self.client.force_login(self.admin)
        response = self.client.post(f"/admin-panel/applications/approve/{application.id}/")
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username="applicant")
        profile = DoctorProfile.objects.get(user=user)
        self.assertEqual(profile.status, DoctorProfile.STATUS_APPROVED)
        self.assertTrue(user.check_password("ApplicantPass1!"))

        application.refresh_from_db()
        self.assertEqual(application.status, DoctorApplication.STATUS_APPROVED)

    def test_rejecting_application_marks_rejected_without_user(self):
        application = DoctorApplication.objects.create(
            username="rejectme",
            email="rejectme@example.com",
        )
        self.client.force_login(self.admin)
        response = self.client.post(f"/admin-panel/applications/reject/{application.id}/")
        self.assertEqual(response.status_code, 302)
        application.refresh_from_db()
        self.assertEqual(application.status, DoctorApplication.STATUS_REJECTED)
        self.assertFalse(User.objects.filter(username="rejectme").exists())

    def test_approval_actions_reject_get_requests(self):
        """CSRF hardening: these endpoints must not fire on plain navigation."""
        application = DoctorApplication.objects.create(
            username="getproof",
            email="getproof@example.com",
        )
        self.client.force_login(self.admin)
        response = self.client.get(f"/admin-panel/applications/approve/{application.id}/")
        self.assertEqual(response.status_code, 405)


class PatientManagementTests(AdminActionTestBase):
    def setUp(self):
        self.patient = User.objects.create_user("managepat", "managepat@example.com", "PatPass2026!")
        ensure_patient_profile(self.patient)

    def test_delete_patient_removes_user(self):
        self.client.force_login(self.admin)
        response = self.client.post(f"/admin-panel/patients/delete/{self.patient.patient_profile.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username="managepat").exists())

    def test_admin_cannot_delete_own_account_via_patient_view(self):
        own_profile = ensure_patient_profile(self.admin)
        self.client.force_login(self.admin)
        response = self.client.post(f"/admin-panel/patients/delete/{own_profile.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

    def test_disable_blocks_login(self):
        self.client.force_login(self.admin)
        response = self.client.post(f"/admin-panel/patients/disable/{self.patient.patient_profile.id}/")
        self.assertEqual(response.status_code, 302)
        self.patient.refresh_from_db()
        self.assertFalse(self.patient.is_active)

        # A disabled account cannot authenticate.
        login_ok = self.client.login(username="managepat", password="PatPass2026!")
        self.assertFalse(login_ok)

    def test_delete_requires_post(self):
        self.client.force_login(self.admin)
        response = self.client.get(f"/admin-panel/patients/delete/{self.patient.patient_profile.id}/")
        self.assertEqual(response.status_code, 405)
        self.assertTrue(User.objects.filter(username="managepat").exists())


class BillingTests(AdminActionTestBase):
    def setUp(self):
        self.patient = User.objects.create_user("billpat", "billpat@example.com", "PatPass2026!")
        ensure_patient_profile(self.patient)

    def test_create_invoice_with_items_and_tax(self):
        self.client.force_login(self.admin)
        response = self.client.post("/admin-panel/billing/create-invoice/", {
            "patient": str(self.patient.patient_profile.id),
            "tax_rate": "13",
            "status": "Unpaid",
            "notes": "Consultation + tests",
            "description[]": ["Consultation", "Blood test"],
            "quantity[]": ["1", "2"],
            "unit_price[]": ["500", "250"],
        })
        self.assertEqual(response.status_code, 302)
        invoice = BillingInvoice.objects.get(patient=self.patient)
        self.assertEqual(invoice.items.count(), 2)
        self.assertEqual(invoice.subtotal, 1000)
        self.assertEqual(invoice.tax_amount, 130)
        self.assertEqual(invoice.grand_total, 1130)
        self.assertEqual(invoice.amount, invoice.grand_total)

    def test_mark_paid_sets_status_and_date(self):
        invoice = BillingInvoice.objects.create(
            patient=self.patient,
            invoice_number="INV-QA-0001",
            amount=500,
            issued_on=timezone.localdate(),
        )
        self.client.force_login(self.admin)
        response = self.client.post(f"/admin-panel/billing/{invoice.id}/mark-paid/")
        self.assertEqual(response.status_code, 302)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, BillingInvoice.STATUS_PAID)
        self.assertEqual(invoice.paid_on, timezone.localdate())

    def test_mark_paid_via_get_is_rejected(self):
        invoice = BillingInvoice.objects.create(
            patient=self.patient,
            invoice_number="INV-QA-0002",
            amount=500,
            issued_on=timezone.localdate(),
        )
        self.client.force_login(self.admin)
        response = self.client.get(f"/admin-panel/billing/{invoice.id}/mark-paid/")
        self.assertEqual(response.status_code, 405)
        invoice.refresh_from_db()
        self.assertNotEqual(invoice.status, BillingInvoice.STATUS_PAID)


class AppointmentAdminTests(AdminActionTestBase):
    def test_appointments_page_loads(self):
        doctor = User.objects.create_user("apptdoc", "apptdoc@example.com", "DocPass2026!")
        DoctorProfile.objects.create(
            user=doctor,
            department=self.department,
            specialization="General",
            status=DoctorProfile.STATUS_APPROVED,
        )
        patient = User.objects.create_user("apptpat", "apptpat@example.com", "PatPass2026!")
        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            department=self.department,
            appointment_date=timezone.localdate() + timedelta(days=2),
            appointment_time="09:00",
            reason="Follow-up",
        )
        self.client.force_login(self.admin)
        response = self.client.get("/admin-panel/appointments/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "apptpat")


class InvoiceModelTests(AdminActionTestBase):
    def test_item_save_recalculates_invoice_totals(self):
        from decimal import Decimal
        patient = User.objects.create_user("modelpat", "modelpat@example.com", "PatPass2026!")
        invoice = BillingInvoice.objects.create(
            patient=patient,
            invoice_number="INV-QA-0003",
            amount=0,
            tax_rate=Decimal("0.13"),
            issued_on=timezone.localdate(),
        )
        InvoiceItem.objects.create(invoice=invoice, description="X-ray", quantity=2, unit_price=Decimal(300))
        invoice.refresh_from_db()
        self.assertEqual(invoice.subtotal, Decimal(600))
        self.assertEqual(invoice.grand_total, Decimal(678))
