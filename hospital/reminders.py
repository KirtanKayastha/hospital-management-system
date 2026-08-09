"""Medicine reminder generation.

Reminder rows are derived from each PrescriptionItem's frequency text so the
patient gets one row per daily dose. Frequency strings are free text entered by
the doctor, so parsing is deliberately forgiving and falls back to a single
morning dose rather than dropping the medicine.
"""

import re
from datetime import time, timedelta

from django.utils import timezone

from admin_nishan.models import MedicineReminder

# Dose slots keyed by how many times per day the medicine is taken.
SLOTS_BY_COUNT = {
    1: [time(8, 0)],
    2: [time(8, 0), time(20, 0)],
    3: [time(8, 0), time(14, 0), time(20, 0)],
    4: [time(8, 0), time(12, 0), time(16, 0), time(20, 0)],
}

MAX_DOSES_PER_DAY = 4


def doses_per_day(frequency):
    """Return how many times per day a frequency string means.

    Handles the common shorthands doctors type: "1-0-1", "twice daily",
    "3 times a day", "TDS". Unknown text yields one dose.
    """
    text = (frequency or "").strip().lower()
    if not text:
        return 1

    # Nepali/Indian shorthand: 1-0-1 means morning-noon-night.
    dash_parts = re.findall(r"\d+", text)
    if re.fullmatch(r"\s*\d+\s*(-\s*\d+\s*)+", text):
        return max(1, sum(1 for part in dash_parts if int(part) > 0))

    words = {
        "once": 1,
        "one": 1,
        "twice": 2,
        "two": 2,
        "bd": 2,
        "bid": 2,
        "thrice": 3,
        "three": 3,
        "tds": 3,
        "tid": 3,
        "four": 4,
        "qid": 4,
        "qds": 4,
    }
    for word, count in words.items():
        if re.search(rf"\b{word}\b", text):
            return count

    match = re.search(r"(\d+)\s*(?:x|times?|/)\s*(?:a\s*)?(?:day|daily)", text)
    if match:
        return min(MAX_DOSES_PER_DAY, max(1, int(match.group(1))))

    if dash_parts:
        return min(MAX_DOSES_PER_DAY, max(1, int(dash_parts[0])))

    return 1


def duration_days(duration):
    """Return the number of days a duration string covers, or None if open ended."""
    text = (duration or "").strip().lower()
    if not text:
        return None
    match = re.search(r"(\d+)", text)
    if not match:
        return None
    value = int(match.group(1))
    if "month" in text:
        return value * 30
    if "week" in text:
        return value * 7
    return value


def build_reminders_for_prescription(prescription):
    """Recreate reminders for every item on a prescription.

    Called after items are written. Existing reminders for the prescription are
    cleared first so an edited prescription never leaves stale dose rows behind.
    """
    MedicineReminder.objects.filter(item__prescription=prescription).delete()

    start = prescription.prescribed_on or timezone.localdate()
    created = []
    for item in prescription.items.all():
        count = doses_per_day(item.frequency)
        slots = SLOTS_BY_COUNT.get(count, SLOTS_BY_COUNT[1])
        days = duration_days(item.duration)
        end = start + timedelta(days=days - 1) if days else None
        for slot in slots:
            created.append(
                MedicineReminder(
                    patient=prescription.patient,
                    item=item,
                    medicine_name=item.medicine_name,
                    dosage=item.dosage,
                    remind_at=slot,
                    start_date=start,
                    end_date=end,
                    is_active=prescription.is_active,
                )
            )
    if created:
        MedicineReminder.objects.bulk_create(created)
    return len(created)


def due_reminders(user, now=None):
    """Reminders whose slot time has passed today and are not yet marked taken."""
    now = now or timezone.localtime()
    today = now.date()
    reminders = MedicineReminder.objects.filter(
        patient=user, is_active=True, start_date__lte=today
    ).exclude(end_date__lt=today)
    return [
        reminder
        for reminder in reminders
        if reminder.remind_at <= now.time() and reminder.last_taken_on != today
    ]
