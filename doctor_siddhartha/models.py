from django.db import models
from django.conf import settings
from django.utils import timezone


class DoctorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100, blank=True, default='General Physician')
    photo = models.ImageField(upload_to='doctor_photos/', blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"


class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]

    patient_id = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    full_name = models.CharField(max_length=150)
    age = models.PositiveIntegerField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    contact_number = models.CharField(max_length=20)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    medical_history = models.TextField(blank=True, help_text="Free-text clinical history / notes")
    assigned_doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['full_name']

    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = f"MC-{timezone.now().strftime('%y%m')}-{Patient.objects.count() + 1:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.patient_id})"

    @property
    def latest_vitals(self):
        return self.vitals.order_by('-recorded_at').first()

    @property
    def last_visit(self):
        last = self.appointments.filter(status='completed').order_by('-date', '-start_time').first()
        return last.date if last else None

    @property
    def next_appointment(self):
        return self.appointments.filter(
            date__gte=timezone.now().date()
        ).exclude(status='cancelled').order_by('date', 'start_time').first()


class Vitals(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vitals')
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    blood_pressure = models.CharField(max_length=15, blank=True, help_text="e.g. 128/84")
    heart_rate = models.PositiveIntegerField(blank=True, null=True, help_text="bpm")
    spo2 = models.PositiveIntegerField(blank=True, null=True, help_text="%")
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        verbose_name_plural = 'Vitals'

    def __str__(self):
        return f"Vitals for {self.patient} @ {self.recorded_at:%Y-%m-%d %H:%M}"


class Appointment(models.Model):
    TYPE_CHOICES = [
        ('consultation', 'Consultation'), ('follow_up', 'Follow-up'),
        ('checkup', 'Checkup'), ('urgent', 'Urgent'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('confirmed', 'Confirmed'),
        ('completed', 'Completed'), ('cancelled', 'Cancelled'),
    ]

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='consultation')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.patient.full_name} - {self.date} {self.start_time}"


class Availability(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
        (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration_minutes = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('doctor', 'day_of_week', 'start_time')
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class Prescription(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    diagnosis = models.TextField()
    additional_notes = models.TextField(blank=True)
    date_issued = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date_issued']

    def __str__(self):
        return f"Prescription for {self.patient.full_name} on {self.date_issued}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=50, help_text="e.g. 500mg")
    frequency = models.CharField(max_length=100, help_text="e.g. Twice daily")
    duration = models.CharField(max_length=50, help_text="e.g. 30 Days")
    refills_remaining = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.medicine_name} ({self.dosage})"