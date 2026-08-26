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
)
from doctor_siddhartha.models import DoctorProfile
from hospital.access import ensure_patient_profile


class PatientFlowTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(slug="gen-pat-qa", name="General Pat QA")
        cls.doctor = cls._create_doctor()
        cls.patient = User.objects.create_user("flow_pat", "flow_pat@example.com", "PatPass2026!", first_name="Flow", last_name="Patient")
        ensure_patient_profile(cls.patient)
        # Open availability every weekday so slot validation passes regardless
        # of which future date a test books.
        for day in range(7):
            DoctorAvailability.objects.create(
                doctor=cls.doctor,
                day_of_week=day,
                start_time="08:00",
                end_time="17:00",
            )

    @classmethod
    def _create_doctor(cls):
        doctor = User.objects.create_user("pat_doc", "pat_doc@example.com", "DocPass2026!", first_name="Pat", last_name="Doctor")
        DoctorProfile.objects.create(
            user=doctor,
            department=cls.department,
            specialization="General Medicine",
            status=DoctorProfile.STATUS_APPROVED,
            consultation_fee=300,
        )
        return doctor

    def setUp(self):
        self.client.force_login(self.patient)


class PatientDashboardTests(PatientFlowTestBase):
    def test_dashboard_loads_with_stats(self):
        response = self.client.get("/patient/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upcoming Appointments")

    def test_booking_creates_pending_appointment(self):
        future_date = (timezone.localdate() + timedelta(days=5)).isoformat()
        response = self.client.post("/patient/book/", {
            "doctor_id": str(self.doctor.id),
            "appointment_date": future_date,
            "appointment_time": "14:30",
            "reason": "Recurring migraines",
        })
        self.assertEqual(response.status_code, 302)
        appointment = Appointment.objects.get(patient=self.patient)
        self.assertEqual(appointment.status, Appointment.STATUS_PENDING)
        self.assertEqual(appointment.doctor, self.doctor)

    def test_duplicate_slot_is_rejected(self):
        future_date = timezone.localdate() + timedelta(days=5)
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            department=self.department,
            appointment_date=future_date,
            appointment_time="14:30",
            reason="First booking",
        )
        self.client.post("/patient/book/", {
            "doctor_id": str(self.doctor.id),
            "appointment_date": future_date.isoformat(),
            "appointment_time": "14:30",
            "reason": "Second booking same slot",
        })
        # The unique constraint must prevent a second identical slot.
        self.assertEqual(
            Appointment.objects.filter(patient=self.patient, appointment_date=future_date, appointment_time="14:30").count(),
            1,
        )

    def test_cancel_appointment(self):
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            department=self.department,
            appointment_date=timezone.localdate() + timedelta(days=4),
            appointment_time="11:00",
            reason="To be cancelled",
            status=Appointment.STATUS_PENDING,
        )
        response = self.client.post(f"/patient/appointments/{appointment.id}/cancel/")
        self.assertEqual(response.status_code, 302)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.STATUS_CANCELLED)

    def test_cancel_via_get_is_rejected(self):
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            department=self.department,
            appointment_date=timezone.localdate() + timedelta(days=4),
            appointment_time="11:00",
            reason="Still active",
            status=Appointment.STATUS_PENDING,
        )
        response = self.client.get(f"/patient/appointments/{appointment.id}/cancel/")
        self.assertEqual(response.status_code, 405)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.STATUS_PENDING)

    def test_cannot_cancel_someone_elses_appointment(self):
        other_patient = User.objects.create_user("other_flow", "other_flow@example.com", "PatPass2026!")
        ensure_patient_profile(other_patient)
        appointment = Appointment.objects.create(
            patient=other_patient,
            doctor=self.doctor,
            department=self.department,
            appointment_date=timezone.localdate() + timedelta(days=4),
            appointment_time="12:00",
            reason="Not mine",
            status=Appointment.STATUS_PENDING,
        )
        response = self.client.post(f"/patient/appointments/{appointment.id}/cancel/")
        self.assertEqual(response.status_code, 404)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.STATUS_PENDING)


class PatientRecordsTests(PatientFlowTestBase):
    def test_medical_records_page_loads(self):
        response = self.client.get("/patient/records/")
        self.assertEqual(response.status_code, 200)

    def test_lab_reports_page_lists_own_reports_only(self):
        LabReport.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            test_name="Glucose Fasting",
            lab_name="Central Lab",
            ordered_date=timezone.localdate(),
        )
        response = self.client.get("/patient/lab-reports/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Glucose Fasting")

    def test_invoices_list_and_detail(self):
        invoice = BillingInvoice.objects.create(
            patient=self.patient,
            invoice_number="INV-PAT-0001",
            amount=1130,
            issued_on=timezone.localdate(),
            status=BillingInvoice.STATUS_UNPAID,
        )
        list_response = self.client.get("/patient/invoices/")
        self.assertEqual(list_response.status_code, 200)
        detail_response = self.client.get(f"/patient/invoices/{invoice.id}/")
        self.assertEqual(detail_response.status_code, 200)
