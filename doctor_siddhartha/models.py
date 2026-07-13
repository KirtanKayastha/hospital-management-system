from django.conf import settings
from django.db import models


class DoctorProfile(models.Model):
	STATUS_PENDING = "Pending"
	STATUS_ACTIVE = "Active"
	STATUS_INACTIVE = "Inactive"
	STATUS_ON_LEAVE = "On Leave"

	STATUS_CHOICES = [
		(STATUS_PENDING, "Pending"),
		(STATUS_ACTIVE, "Active"),
		(STATUS_INACTIVE, "Inactive"),
		(STATUS_ON_LEAVE, "On Leave"),
	]

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile")
	department = models.ForeignKey("admin_nishan.Department", on_delete=models.PROTECT, related_name="doctors")
	specialization = models.CharField(max_length=120)
	qualification = models.CharField(max_length=200, blank=True)
	experience_years = models.PositiveSmallIntegerField(default=0)
	license_number = models.CharField(max_length=60, blank=True)
	phone = models.CharField(max_length=20, blank=True)
	consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	bio = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["user__username"]

	def __str__(self):
		return f"{self.user.get_full_name() or self.user.username} - {self.specialization}"

	@property
	def initials(self):
		name = self.user.get_full_name() or self.user.username
		parts = name.split()
		if not parts:
			return "D"
		if len(parts) == 1:
			return parts[0][:2].upper()
		return f"{parts[0][0]}{parts[-1][0]}".upper()

	@property
	def display_name(self):
		return self.user.get_full_name() or self.user.username

	@property
	def available_day_labels(self):
		day_map = {
			0: "Monday",
			1: "Tuesday",
			2: "Wednesday",
			3: "Thursday",
			4: "Friday",
			5: "Saturday",
			6: "Sunday",
		}
		days = self.user.availability_slots.filter(is_active=True).values_list("day_of_week", flat=True).distinct()
		return [day_map.get(day, str(day)) for day in days]


class DoctorNote(models.Model):
	doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_notes")
	title = models.CharField(max_length=150)
	body = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return self.title
