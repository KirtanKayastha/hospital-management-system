from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from admin_nishan.models import (
    Appointment,
    BillingInvoice,
    Department,
    DoctorAvailability,
    LabReport,
    Notification,
)
from hospital.access import ensure_patient_profile


class DoctorWorkflowTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(slug="cardio-qa", name="Cardiology QA")
        cls.doctor = User.objects.create_user("qa_doc", "qa_doc@example.com", "DocPass2026!", first_name="QA", last_name="Doctor")
        from doctor_siddhartha.models import DoctorProfile
        DoctorProfile.objects.create(
            user=cls.doctor,
            department=cls.department,
            specialization="Cardiology",
            status=DoctorProfile.STATUS_APPROVED,
            consultation_fee=500,
        )
        cls.patient = User.objects.create_user("qa_pat", "qa_pat@example.com", "PatPass2026!", first_name="QA", last_name="Patient")
        ensure_patient_profile(cls.patient)

    def _make_appointment(self, days_ahead=3):
        return Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            department=self.department,
            appointment_date=timezone.localdate() + timedelta(days=days_ahead),
            appointment_time="10:30",
            reason="Chest pain on exertion",
            status=Appointment.STATUS_PENDING,
        )


class AppointmentDecisionTests(DoctorWorkflowTestBase):
    def test_approve_confirms_and_creates_single_invoice(self):
        appointment = self._make_appointment()
        self.client.force_login(self.doctor)

        response = self.client.post(f"/doctor/appointments/approve/{appointment.id}/")
        self.assertEqual(response.status_code, 302)

        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.STATUS_CONFIRMED)
        invoices = BillingInvoice.objects.filter(appointment=appointment)
        self.assertEqual(invoices.count(), 1)
        self.assertEqual(invoices.first().amount, 500)
        # Patient gets notified.
        self.assertTrue(Notification.objects.filter(recipient=self.patient).exists())

        # Double submit must not bill twice.
        self.client.post(f"/doctor/appointments/approve/{appointment.id}/")
        self.assertEqual(BillingInvoice.objects.filter(appointment=appointment).count(), 1)

    def test_approve_via_get_is_rejected(self):
        """State changes must not be triggerable by a plain link (CSRF)."""
        appointment = self._make_appointment()
        self.client.force_login(self.doctor)
        response = self.client.get(f"/doctor/appointments/approve/{appointment.id}/")
        self.assertEqual(response.status_code, 405)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.STATUS_PENDING)

    def test_reject_cancels_and_notifies(self):
        appointment = self._make_appointment()
        self.client.force_login(self.doctor)
        response = self.client.post(f"/doctor/appointments/reject/{appointment.id}/")
        self.assertEqual(response.status_code, 302)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.STATUS_CANCELLED)
        self.assertTrue(Notification.objects.filter(recipient=self.patient).exists())

    def test_other_doctors_appointments_are_invisible(self):
        other_doctor = User.objects.create_user("other_doc", "other@example.com", "DocPass2026!")
        from doctor_siddhartha.models import DoctorProfile
        DoctorProfile.objects.create(
            user=other_doctor,
            department=self.department,
            specialization="General",
            status=DoctorProfile.STATUS_APPROVED,
        )
        appointment = self._make_appointment()
        self.client.force_login(other_doctor)
        response = self.client.post(f"/doctor/appointments/approve/{appointment.id}/")
        self.assertEqual(response.status_code, 404)


class ScheduleTests(DoctorWorkflowTestBase):
    def test_add_and_delete_availability(self):
        self.client.force_login(self.doctor)
        response = self.client.post("/doctor/schedule/", {
            "day_of_week": "1",
            "start_time": "09:00",
            "end_time": "17:00",
        })
        self.assertEqual(response.status_code, 302)
        slot = DoctorAvailability.objects.get(doctor=self.doctor, day_of_week=1)
        self.assertEqual(slot.start_time.strftime("%H:%M"), "09:00")

        response = self.client.post(f"/doctor/schedule/delete/{slot.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(DoctorAvailability.objects.filter(id=slot.id).exists())


class LabReportTests(DoctorWorkflowTestBase):
    def test_lab_reports_page_lists_ordered_reports(self):
        LabReport.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            test_name="CBC",
            lab_name="Central Lab",
            ordered_date=timezone.localdate(),
        )
        self.client.force_login(self.doctor)
        response = self.client.get("/doctor/lab-reports/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CBC")

    def test_lab_report_update_requires_post(self):
        report = LabReport.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            test_name="Lipid Panel",
            lab_name="Central Lab",
            ordered_date=timezone.localdate(),
        )
        self.client.force_login(self.doctor)
        response = self.client.post("/doctor/lab-reports/", {
            "report_id": report.id,
            "status": "Ready",
            "summary": "All values within range.",
        })
        self.assertEqual(response.status_code, 302)
        report.refresh_from_db()
        self.assertEqual(report.status, "Ready")


class DashboardTests(DoctorWorkflowTestBase):
    def test_dashboard_loads_for_approved_doctor(self):
        self.client.force_login(self.doctor)
        response = self.client.get("/doctor/dashboard/")
        self.assertEqual(response.status_code, 200)

    def test_pending_doctor_is_bounced_to_login(self):
        from doctor_siddhartha.models import DoctorProfile
        pending_doc = User.objects.create_user("pending_doc", "pending@example.com", "DocPass2026!")
        DoctorProfile.objects.create(
            user=pending_doc,
            department=self.department,
            specialization="General",
            status=DoctorProfile.STATUS_PENDING,
        )
        self.client.force_login(pending_doc)
        response = self.client.get("/doctor/dashboard/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])
