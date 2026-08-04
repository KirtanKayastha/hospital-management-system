#!/usr/bin/env python
import os
import sys
import random
from datetime import date, time, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital.settings")

import django
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from admin_nishan.models import (
    Appointment,
    Department,
    DoctorAvailability,
    MedicalRecord,
    Prescription,
    PrescriptionItem,
)
from doctor_siddhartha.models import DoctorProfile
from patient_roshan.models import PatientProfile

User = get_user_model()

random.seed(42)


def banner(text):
    width = 60
    print("\n" + "=" * width)
    print(f"  {text}")
    print("=" * width)


def create_departments():
    departments = []
    data = [
        ("Cardiology", "cardiology", "Heart and cardiovascular care"),
        ("Neurology", "neurology", "Brain and nervous system disorders"),
        ("Pediatrics", "pediatrics", "Children's health and medical care"),
        ("Orthopedics", "orthopedics", "Bones, joints, and musculoskeletal care"),
        ("Dermatology", "dermatology", "Skin, hair, and nail conditions"),
        ("Ophthalmology", "ophthalmology", "Eye care and vision services"),
    ]
    for name, slug, description in data:
        dept, created = Department.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "description": description, "is_active": True},
        )
        departments.append(dept)
        if created:
            print(f"  [NEW] Department: {name}")
    return departments


def create_doctors(departments):
    doctors = []
    specialties = {
        "doctor1": ("Cardiology", "MD, FACC"),
        "doctor2": ("Neurology", "MD, PhD"),
        "doctor3": ("Pediatrics", "MD, DCh"),
        "doctor4": ("Orthopedics", "MD, FRCS"),
        "doctor5": ("Dermatology", "MD, DM"),
    }
    for i in range(1, 6):
        username = f"doctor{i}"
        email = f"doctor{i}@gmail.com"
        password = f"doctor{i}"
        specialization, qualification = specialties[username]
        dept = departments[i - 1]

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": specialization.split()[0],
                "last_name": f"Doctor{i}",
                "is_active": True,
                "is_staff": True,
            },
        )
        if created or not user.has_usable_password():
            user.set_password(password)
            user.save()

        doc, created = DoctorProfile.objects.get_or_create(
            user=user,
            defaults={
                "department": dept,
                "specialization": specialization,
                "qualification": qualification,
                "experience_years": random.randint(3, 25),
                "license_number": f"LIC-{random.randint(100000, 999999)}",
                "phone": f"+1-555-020{i}",
                "consultation_fee": random.choice([0, 50, 75, 100, 150, 200]),
                "bio": f"Experienced {specialization} doctor with {random.randint(3, 25)} years of practice.",
                "status": DoctorProfile.STATUS_APPROVED,
            },
        )
        doctors.append(doc)
        if created:
            print(f"  [NEW] Doctor: {username} ({specialization})")
    return doctors


def create_patients():
    patients = []
    blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    genders = ["Male", "Female", "Other"]
    streets = ["Main St", "Oak Ave", "Maple Rd", "Cedar Ln", "Pine Dr", "Elm Blvd"]

    for i in range(1, 11):
        username = f"patient{i}"
        email = f"patient{i}@gmail.com"
        password = f"patient{i}"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": f"Patient",
                "last_name": f"Number{i}",
                "is_active": True,
            },
        )
        if created or not user.has_usable_password():
            user.set_password(password)
            user.save()

        dob = date(1970 + random.randint(0, 35), random.randint(1, 12), random.randint(1, 28))
        profile, created = PatientProfile.objects.get_or_create(
            user=user,
            defaults={
                "phone": f"+1-555-010{i}",
                "dob": dob,
                "gender": random.choice(genders),
                "blood_group": random.choice(blood_groups),
                "address": f"{random.randint(100, 999)} {random.choice(streets)}, City {i}",
            },
        )
        patients.append(profile)
        if created:
            print(f"  [NEW] Patient: {username}")
    return patients


def create_availability(doctors):
    day_choices = [0, 1, 2, 3, 4]
    start_times = [time(8, 0), time(9, 0), time(10, 0)]
    count = 0
    for doctor in doctors:
        for day in random.sample(day_choices, k=random.randint(3, 5)):
            start = random.choice(start_times)
            end_hour = start.hour + random.randint(4, 6)
            end = time(min(end_hour, 17), 0)
            _, created = DoctorAvailability.objects.get_or_create(
                doctor=doctor.user,
                day_of_week=day,
                start_time=start,
                defaults={"end_time": end, "is_active": True, "location": f"Room {random.randint(101, 110)}"},
            )
            if created:
                count += 1
    print(f"  [NEW] Availability slots: {count}")


def create_appointments(patients, doctors, departments):
    reasons = [
        "Regular checkup",
        "Follow-up visit",
        "Chest pain",
        "Headache and dizziness",
        "Knee pain",
        "Skin rash",
        "Fever and cough",
        "Annual physical exam",
        "Back pain",
        "High blood pressure",
    ]
    statuses = [
        Appointment.STATUS_PENDING,
        Appointment.STATUS_CONFIRMED,
        Appointment.STATUS_COMPLETED,
        Appointment.STATUS_CANCELLED,
    ]
    weights = [0.2, 0.35, 0.35, 0.1]

    appointments = []
    for _ in range(30):
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        dept = doctor.department
        appt_date = date.today() + timedelta(days=random.randint(-30, 30))
        hour = random.choice([8, 9, 10, 11, 14, 15])
        appt_time = time(hour=hour, minute=random.choice([0, 30]))

        existing = Appointment.objects.filter(
            doctor=doctor.user,
            appointment_date=appt_date,
            appointment_time=appt_time,
        ).exists()
        if existing:
            continue

        status = random.choices(statuses, weights=weights)[0]
        appt = Appointment.objects.create(
            patient=patient.user,
            doctor=doctor.user,
            department=dept,
            appointment_date=appt_date,
            appointment_time=appt_time,
            reason=random.choice(reasons),
            status=status,
            notes="",
        )
        appointments.append(appt)
    print(f"  [NEW] Appointments: {len(appointments)}")
    return appointments


def create_medical_records(appointments):
    diagnoses = ["Hypertension", "Diabetes Type 2", "Common Cold", "Allergic Rhinitis", "Migraine", "Fracture", "Eczema", "Bronchitis"]
    symptoms_list = ["Headache", "Fever", "Cough", "Pain", "Fatigue", "Nausea", "Dizziness", "Shortness of breath"]
    treatments = ["Medication prescribed", "Rest and hydration", "Physical therapy", "Surgery scheduled", "Lifestyle changes"]
    record_statuses = ["Active", "Resolved", "Follow-up required"]

    completed = [a for a in appointments if a.status == Appointment.STATUS_COMPLETED]
    count = 0
    for appt in completed[:15]:
        MedicalRecord.objects.get_or_create(
            appointment=appt,
            defaults={
                "patient": appt.patient,
                "doctor": appt.doctor,
                "department": appt.department,
                "diagnosis": random.choice(diagnoses),
                "symptoms": random.choice(symptoms_list),
                "treatment": random.choice(treatments),
                "status": random.choice(record_statuses),
                "visit_date": appt.appointment_date,
            },
        )
        count += 1
    print(f"  [NEW] Medical records: {count}")


def create_prescriptions(appointments):
    medicines = [
        ("Amoxicillin", "500mg", "3 times daily", "7 days"),
        ("Paracetamol", "500mg", "2 times daily", "5 days"),
        ("Ibuprofen", "400mg", "3 times daily", "7 days"),
        ("Omeprazole", "20mg", "1 time daily", "14 days"),
        ("Metformin", "500mg", "2 times daily", "30 days"),
        ("Atorvastatin", "10mg", "1 time daily", "30 days"),
        ("Salbutamol", "100mcg", "2 times daily", "7 days"),
        ("Cetirizine", "10mg", "1 time daily", "14 days"),
    ]
    completed = [a for a in appointments if a.status == Appointment.STATUS_COMPLETED]
    count = 0
    for appt in completed[:10]:
        rx = Prescription.objects.create(
            patient=appt.patient,
            doctor=appt.doctor,
            appointment=appt,
            diagnosis="Follow-up consultation",
            notes="Take as prescribed. Follow up in 2 weeks.",
            prescribed_on=appt.appointment_date,
            is_active=True,
        )
        for _ in range(random.randint(1, 3)):
            med = random.choice(medicines)
            PrescriptionItem.objects.create(
                prescription=rx,
                medicine_name=med[0],
                dosage=med[1],
                frequency=med[2],
                duration=med[3],
                instructions="Take after meals.",
            )
        count += 1
    print(f"  [NEW] Prescriptions: {count}")


def print_summary(departments, doctors, patients, appointments):
    banner("SEED SUMMARY")
    print(f"  Departments : {Department.objects.count()}")
    print(f"  Doctors     : {User.objects.filter(is_staff=True).count()}")
    print(f"  Patients    : {PatientProfile.objects.count()}")
    print(f"  Appointments: {Appointment.objects.count()}")
    print(f"  MedicalRecords: {MedicalRecord.objects.count()}")
    print(f"  Prescriptions: {Prescription.objects.count()}")
    print(f"  PrescriptionItems: {PrescriptionItem.objects.count()}")
    print(f"  AvailabilitySlots: {DoctorAvailability.objects.count()}")
    print()
    print("  Demo Credentials:")
    print("  -----------------")
    for i in range(1, 6):
        print(f"  Doctor {i}  : doctor{i} / doctor{i}")
    for i in range(1, 11):
        print(f"  Patient {i} : patient{i} / patient{i}")
    print()
    print("  Admin      : admin / admin123")
    print("=" * 60 + "\n")


def main():
    banner("SEEDING DATABASE")
    print("This script is idempotent. Safe to run multiple times.\n")

    print("[1/6] Creating departments...")
    departments = create_departments()

    print("\n[2/6] Creating doctors...")
    doctors = create_doctors(departments)

    print("\n[3/6] Creating patients...")
    patients = create_patients()

    print("\n[4/6] Creating doctor availability...")
    create_availability(doctors)

    print("\n[5/6] Creating appointments...")
    appointments = create_appointments(patients, doctors, departments)

    print("\n[6/6] Creating medical records and prescriptions...")
    create_medical_records(appointments)
    create_prescriptions(appointments)

    print_summary(departments, doctors, patients, appointments)


if __name__ == "__main__":
    main()
