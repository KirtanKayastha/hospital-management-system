"""Central notification helpers.

Every module writes notifications through `notify()` so the payload shape stays
consistent and a single call site controls de-duplication and delivery rules.
"""

from admin_nishan.models import Notification


def notify(recipient, title, message, category=Notification.CATEGORY_GENERAL, action_url=""):
    """Create one notification. Returns None when there is no recipient.

    Views often hold a nullable FK (Appointment.doctor is SET_NULL), so guarding
    here keeps every call site from repeating the same check.
    """
    if recipient is None:
        return None
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        category=category,
        action_url=action_url or "",
    )


def notify_appointment(recipient, title, message, appointment=None, action_url=""):
    if not action_url and appointment is not None:
        action_url = f"/patient/appointments/{appointment.id}/"
    return notify(
        recipient,
        title,
        message,
        category=Notification.CATEGORY_APPOINTMENT,
        action_url=action_url,
    )


def unread_count(user):
    if not user or not user.is_authenticated:
        return 0
    return Notification.objects.filter(recipient=user, is_read=False).count()


def notification_context(request):
    """Context processor: expose unread notifications to every template.

    Base templates render the navbar bell, so the count has to be available
    without every view remembering to pass it.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"unread_notification_count": 0, "navbar_notifications": []}
    unread = Notification.objects.filter(recipient=user, is_read=False)
    return {
        "unread_notification_count": unread.count(),
        "navbar_notifications": list(unread[:5]),
    }
