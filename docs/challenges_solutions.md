# Challenges & Solutions

## 1. Technical Challenges Faced

### Challenge 1: Role-Based Access Control Implementation

**Problem:** Implementing a clean, maintainable role-based access control system across multiple Django apps without duplicating code.

**Solution:** Created a centralized `hospital/access.py` module with decorators:
- `@patient_required`
- `@doctor_required`
- `@admin_required`

These decorators check the user's `user_type` field and redirect unauthorized users. This approach ensures consistent access control across all modules.

**Key Learning:** Centralizing authentication logic in a shared module prevents code duplication and makes maintenance easier.

---

### Challenge 2: Automatic Medicine Reminder Generation

**Problem:** Converting free-text frequency strings (like "3 times daily", "1-0-1", "Every 8 hours") into concrete reminder time slots.

**Solution:** Created `hospital/reminders.py` with a robust parsing engine:
- Parses common patterns: "1-0-1" (Nepali/Indian shorthand), "twice daily", "TDS", "3 times a day"
- Falls back to a single morning dose for unrecognized patterns
- Generates 1-4 time slots based on frequency
- Clears old reminders before regenerating to prevent duplicates

**Key Learning:** Healthcare data is messy. Build forgiving parsers that make reasonable defaults rather than failing on unexpected input.

---

### Challenge 3: Prescription-MedicineReminder Data Integrity

**Problem:** When a doctor edits a prescription, old MedicineReminder rows became stale, leading to duplicate or incorrect reminders.

**Solution:** Implemented a "clear and regenerate" strategy in `build_reminders_for_prescription()`:
1. Delete all existing reminders for the prescription
2. Parse each PrescriptionItem's frequency
3. Generate new reminder slots
4. Bulk create all new reminders

**Key Learning:** For derived data, it's often safer to rebuild from source than to patch incrementally.

---

### Challenge 4: Database Transaction Isolation in Tests

**Problem:** Test data was leaking between tests because `transaction.savepoint()` was a no-op when `AUTOCOMMIT=False` was set.

**Solution:** Used Django's `set_autocommit(False)` with explicit `rollback()` instead of savepoints:
```python
from django.db import transaction

def setUp(self):
    transaction.set_autocommit(False)

def tearDown(self):
    transaction.rollback()
    transaction.set_autocommit(True)
```

**Key Learning:** Django's transaction management behaves differently in test mode. Always verify database state between tests.

---

### Challenge 5: Cloudinary Media Storage Configuration

**Problem:** Profile pictures were not uploading correctly to Cloudinary. The default Django file storage was being used instead.

**Solution:** Properly configured Cloudinary as the default file storage:
```python
INSTALLED_APPS = [
    'cloudinary',
    'cloudinary_storage',
]

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
}
```

**Key Learning:** Third-party storage backends require both package installation AND explicit configuration in settings.

---

### Challenge 6: Mailgun Email Integration

**Problem:** Password reset emails were not being sent due to SMTP configuration issues.

**Solution:** Switched from SMTP to Mailgun's HTTP API via `django-anymail`:
```python
EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'

ANYMAIL = {
    'MAILGUN_API_KEY': os.environ.get('MAILGUN_API_KEY'),
    'MAILGUN_SENDER_DOMAIN': os.environ.get('MAILGUN_DOMAIN'),
}
```

**Key Learning:** HTTP-based email APIs (like Mailgun) are more reliable than SMTP for serverless deployments.

---

### Challenge 7: Template Inheritance and Context Variables

**Problem:** Child templates couldn't access parent template's context variables when using `{% with %}` blocks.

**Solution:** Passed required context variables explicitly from views and avoided relying on parent template context in child templates:
```python
# In view
context = {
    'doctor_profile': doctor_profile,
    'active_page': 'dashboard',
}

# In template
{% with active_page='dashboard' %}
```

**Key Learning:** Django template context is not inherited the way one might expect. Always pass what you need explicitly.

---

### Challenge 8: Doctor Profile Access Pattern

**Problem:** Multiple views were inconsistently accessing the doctor profile (some used `doctor_profile`, others used `profile`).

**Solution:** Standardized on `request.user.doctor_profile` (Django's reverse OneToOne accessor) and passed `doctor_profile` consistently in all doctor views:
```python
doctor_profile = request.user.doctor_profile
context = {'doctor_profile': doctor_profile, ...}
```

**Key Learning:** Django's reverse OneToOne accessor (`user.profile`) is cleaner than separate queries and avoids N+1 problems.

---

### Challenge 9: Notification System Architecture

**Problem:** Notifications were scattered across multiple views with inconsistent formatting and no centralized management.

**Solution:** Created `hospital/notifications.py` with helper functions:
- `notify()` - Generic notification creator
- `notify_appointment()` - Appointment-specific notification
- `notification_context()` - Context processor for unread count

Used a context processor to inject unread notification count globally:
```python
# settings.py
TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            'hospital.notifications.notification_context',
        ],
    },
}]
```

**Key Learning:** Context processors are ideal for injecting global data (like notification counts) without modifying every view.

---

### Challenge 10: Git Branch Conflicts

**Problem:** Multiple team members working on `settings.py` caused merge conflicts.

**Solution:** Established clear ownership:
- `settings.py` - Team lead (Kirtan) manages
- Feature branches for each module
- Regular sync with main branch

**Key Learning:** For collaborative projects, establish clear file ownership and use feature branches to avoid merge conflicts.

---

## 11. Key Learnings Summary

| Area | Learning |
|------|----------|
| Architecture | Centralize cross-cutting concerns (auth, notifications) in shared modules |
| Database | Use Django ORM properly to avoid N+1 queries and ensure data integrity |
| Testing | Test isolation requires careful transaction management |
| Deployment | Cloud services (Cloudinary, Mailgun) need explicit configuration beyond package installation |
| Teamwork | Clear ownership and communication prevent merge conflicts |
| Healthcare Software | Input validation must be forgiving - medical data is messy |
| Django | Template context is not inherited; always pass explicitly |
| Signals | Use post_save signals for automatic side effects (like reminder generation) |
