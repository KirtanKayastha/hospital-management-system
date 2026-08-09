from django.conf import settings
from django.db import models
from django.utils import timezone


class Department(models.Model):
	name = models.CharField(max_length=120, unique=True)
	slug = models.SlugField(max_length=140, unique=True)
	description = models.TextField(blank=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return self.name

	@property
	def display_name(self):
		return self.name


class DoctorAvailability(models.Model):
	DAY_CHOICES = [
		(0, "Monday"),
		(1, "Tuesday"),
		(2, "Wednesday"),
		(3, "Thursday"),
		(4, "Friday"),
		(5, "Saturday"),
		(6, "Sunday"),
	]

	doctor = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="availability_slots",
	)
	day_of_week = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
	start_time = models.TimeField()
	end_time = models.TimeField()
	is_active = models.BooleanField(default=True)
	location = models.CharField(max_length=120, blank=True)

	class Meta:
		ordering = ["day_of_week", "start_time"]

	def __str__(self):
		return f"{self.doctor.username} - {self.get_day_of_week_display()}"

	@property
	def day_label(self):
		return self.get_day_of_week_display()


class Appointment(models.Model):
	STATUS_PENDING = "Pending"
	STATUS_CONFIRMED = "Confirmed"
	STATUS_COMPLETED = "Completed"
	STATUS_CANCELLED = "Cancelled"
	STATUS_NO_SHOW = "No Show"

	STATUS_CHOICES = [
		(STATUS_PENDING, "Pending"),
		(STATUS_CONFIRMED, "Confirmed"),
		(STATUS_COMPLETED, "Completed"),
		(STATUS_CANCELLED, "Cancelled"),
		(STATUS_NO_SHOW, "No Show"),
	]

	patient = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="patient_appointments",
	)
	doctor = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="doctor_appointments",
	)
	department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="appointments")
	appointment_date = models.DateField()
	appointment_time = models.TimeField()
	reason = models.TextField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-appointment_date", "-appointment_time", "-created_at"]
		unique_together = [("doctor", "appointment_date", "appointment_time")]

	def __str__(self):
		return f"{self.patient.username} with {self.doctor.username} on {self.appointment_date}"

	@property
	def patient_name(self):
		return self.patient.get_full_name() or self.patient.username

	@property
	def doctor_name(self):
		return self.doctor.get_full_name() or self.doctor.username

	@property
	def doctor_initials(self):
		name = self.doctor_name.split()
		return (name[0][:1] + (name[-1][:1] if len(name) > 1 else name[0][1:2])).upper()

	@property
	def patient_initials(self):
		name = self.patient_name.split()
		return (name[0][:1] + (name[-1][:1] if len(name) > 1 else name[0][1:2])).upper()

	@property
	def department_name(self):
		return self.department.name

	@property
	def display_date(self):
		return self.appointment_date.strftime("%b %d, %Y")

	@property
	def display_time(self):
		return self.appointment_time.strftime("%I:%M %p")

	@property
	def time_value(self):
		return self.appointment_time.strftime("%H:%M")

	@property
	def date(self):
		return self.display_date

	@property
	def time(self):
		return self.display_time


class MedicalRecord(models.Model):
	STATUS_STABLE = "Stable"
	STATUS_RESOLVED = "Resolved"
	STATUS_MONITORING = "Monitoring"
	STATUS_CRITICAL = "Critical"

	STATUS_CHOICES = [
		(STATUS_STABLE, "Stable"),
		(STATUS_RESOLVED, "Resolved"),
		(STATUS_MONITORING, "Monitoring"),
		(STATUS_CRITICAL, "Critical"),
	]

	patient = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="medical_records",
	)
	doctor = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="authored_medical_records",
	)
	appointment = models.OneToOneField(
		Appointment,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="medical_record",
	)
	department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="medical_records")
	diagnosis = models.CharField(max_length=200)
	symptoms = models.TextField(blank=True)
	treatment = models.TextField(blank=True)
	notes = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_STABLE)
	follow_up_date = models.DateField(null=True, blank=True)
	visit_date = models.DateField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-visit_date", "-created_at"]

	def __str__(self):
		return f"{self.patient.username} - {self.diagnosis}"

	@property
	def doctor_name(self):
		return self.doctor.get_full_name() if self.doctor else "Unassigned"

	@property
	def doctor_specialization(self):
		profile = getattr(self.doctor, "doctor_profile", None)
		return profile.specialization if profile else "General"

	@property
	def display_date(self):
		return self.visit_date.strftime("%b %d, %Y")

	@property
	def display_time(self):
		return self.created_at.strftime("%I:%M %p")

	@property
	def status_color(self):
		if self.status == self.STATUS_CRITICAL:
			return "error"
		if self.status == self.STATUS_RESOLVED:
			return "outline"
		return "secondary"

	@property
	def date(self):
		return self.display_date

	@property
	def time(self):
		return self.display_time

	@property
	def color(self):
		return self.status_color


class Prescription(models.Model):
	patient = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="prescriptions",
	)
	doctor = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="authored_prescriptions",
	)
	appointment = models.ForeignKey(  # ✅ FIXED: Changed from OneToOneField to ForeignKey
		Appointment,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="prescriptions",  # ✅ FIXED: changed from "prescription" to "prescriptions"
	)
	diagnosis = models.CharField(max_length=200)
	notes = models.TextField(blank=True)
	prescribed_on = models.DateField()
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-prescribed_on", "-created_at"]

	def __str__(self):
		return f"Prescription for {self.patient.username}"

	@property
	def primary_medicine(self):
		item = self.items.first()
		return item.medicine_name if item else "Prescription"

	@property
	def refill_date(self):
		return self.prescribed_on.strftime("%b %d, %Y")

	@property
	def medicine(self):
		return self.primary_medicine


class PrescriptionItem(models.Model):
	prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
	medicine_name = models.CharField(max_length=150)
	dosage = models.CharField(max_length=100)
	frequency = models.CharField(max_length=100)
	duration = models.CharField(max_length=100)
	instructions = models.TextField(blank=True)

	class Meta:
		ordering = ["id"]

	def __str__(self):
		return self.medicine_name


class LabReport(models.Model):
	STATUS_PENDING = "Pending"
	STATUS_READY = "Ready"
	STATUS_REVIEW = "In Review"

	STATUS_CHOICES = [
		(STATUS_PENDING, "Pending"),
		(STATUS_READY, "Ready"),
		(STATUS_REVIEW, "In Review"),
	]

	patient = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="lab_reports",
	)
	doctor = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="ordered_lab_reports",
	)
	appointment = models.ForeignKey(
		Appointment,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="lab_reports",
	)
	test_name = models.CharField(max_length=160)
	lab_name = models.CharField(max_length=160)
	ordered_on = models.DateField()
	result_date = models.DateField(null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
	report_url = models.URLField(blank=True)
	summary = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-ordered_on", "-created_at"]

	def __str__(self):
		return f"{self.test_name} - {self.patient.username}"

	@property
	def file_link(self):
		return self.report_url

	@property
	def display_date(self):
		return self.ordered_on.strftime("%b %d, %Y")

	@property
	def date(self):
		return self.display_date

	@property
	def file_url(self):
		return self.report_url

	@property
	def ordered_by(self):
		return self.doctor.get_full_name() if self.doctor else "Unknown"


class BillingInvoice(models.Model):
	STATUS_DRAFT = "Draft"
	STATUS_UNPAID = "Unpaid"
	STATUS_PAID = "Paid"
	STATUS_VOID = "Void"

	STATUS_CHOICES = [
		(STATUS_DRAFT, "Draft"),
		(STATUS_UNPAID, "Unpaid"),
		(STATUS_PAID, "Paid"),
		(STATUS_VOID, "Void"),
	]

	invoice_number = models.CharField(max_length=30, unique=True)
	patient = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="billing_invoices",
	)
	appointment = models.ForeignKey(
		Appointment,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="billing_invoices",
	)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UNPAID)
	issued_on = models.DateField()
	due_on = models.DateField(null=True, blank=True)
	paid_on = models.DateField(null=True, blank=True)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-issued_on", "-created_at"]

	def __str__(self):
		return self.invoice_number

	@property
	def display_amount(self):
		return f"${self.amount:,.2f}"


class MedicineReminder(models.Model):
	"""A daily dose slot generated from a PrescriptionItem.

	Reminders are derived rows rather than a computed property so a patient can
	mark an individual dose as taken without mutating the prescription.
	"""

	patient = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="medicine_reminders",
	)
	item = models.ForeignKey(
		PrescriptionItem,
		on_delete=models.CASCADE,
		related_name="reminders",
	)
	medicine_name = models.CharField(max_length=150)
	dosage = models.CharField(max_length=100, blank=True)
	remind_at = models.TimeField()
	start_date = models.DateField()
	end_date = models.DateField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
	last_taken_on = models.DateField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["remind_at", "medicine_name"]

	def __str__(self):
		return f"{self.medicine_name} @ {self.remind_at}"

	@property
	def taken_today(self):
		return self.last_taken_on == timezone.localdate()

	@property
	def display_time(self):
		return self.remind_at.strftime("%I:%M %p").lstrip("0")


class Notification(models.Model):
	CATEGORY_GENERAL = "General"
	CATEGORY_APPOINTMENT = "Appointment"
	CATEGORY_LAB = "Lab"
	CATEGORY_BILLING = "Billing"

	CATEGORY_CHOICES = [
		(CATEGORY_GENERAL, "General"),
		(CATEGORY_APPOINTMENT, "Appointment"),
		(CATEGORY_LAB, "Lab"),
		(CATEGORY_BILLING, "Billing"),
	]

	recipient = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="notifications",
	)
	title = models.CharField(max_length=200)
	message = models.TextField()
	category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_GENERAL)
	is_read = models.BooleanField(default=False)
	action_url = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return self.title