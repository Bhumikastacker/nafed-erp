# Copyright (c) 2026, CSM Technologies Pvt Ltd
# For license information, please see license.txt

import frappe
from frappe.utils import now, get_url, add_days, nowdate

# ====================================================
# MAIN DISPATCH FUNCTION (ENTRY POINT)
# ====================================================
def notify_case_event(case_id, event_type, message, link=None):
    """
    Called whenever a case event occurs
    (Status Change / Hearing / Order / Reminder etc.)
    """

    case_link = link or f"{get_url()}/app/legal-case-registration/{case_id}"
    recipients = get_notification_recipients(event_type)

    for r in recipients:
        try:
            if r["digest_mode"]:
                queue_digest_notification(
                    case_id=case_id,
                    event_type=event_type,
                    recipient=r["recipient"],
                    channel=r["channel"],
                    message=message,
                    link=case_link
                )
            else:
                send_immediate_notification(
                    case_id=case_id,
                    event_type=event_type,
                    recipient=r["recipient"],
                    channel=r["channel"],
                    message=message,
                    link=case_link
                )

        except Exception as e:
            log_notification(
                case_id=case_id,
                event_type=event_type,
                recipient=r["recipient"],
                channel=r["channel"],
                status="Failed",
                error=str(e)
            )


# ====================================================
# RECIPIENT RESOLUTION
# ====================================================
def get_notification_recipients(event_type):
    """
    Reads Legal Case Notification Preference
    Uses digest_mode (checkbox)
    """

    prefs = frappe.get_all(
        "Legal Case Notification Preference",
        filters={
            "event_type": event_type
        },
        fields=[
            "user",
            "advocate",
            "channel",
            "digest_mode"
        ]
    )

    recipients = []

    for p in prefs:
        target = p.user or p.advocate
        if not target:
            continue

        recipients.append({
            "recipient": target,
            "channel": p.channel,
            "digest_mode": int(p.digest_mode or 0)
        })

    return recipients


# ====================================================
# IMMEDIATE NOTIFICATIONS
# ====================================================
def send_immediate_notification(case_id, event_type, recipient, channel, message, link):
    """
    Sends notification instantly (Email / Portal / SMS)
    """

    if channel == "Email":
        frappe.sendmail(
            recipients=[recipient],
            subject=f"[Legal Case] {event_type} – {case_id}",
            message=f"""
                <p>{message}</p>
                <p>
                    <a href="{link}">Open Case</a>
                </p>
            """
        )

    elif channel == "Portal":
        frappe.publish_realtime(
            event="legal_case_notification",
            message={
                "case_id": case_id,
                "event_type": event_type,
                "message": message,
                "link": link
            },
            user=recipient
        )

    elif channel == "SMS":
        # SMS gateway integration placeholder
        pass

    log_notification(
        case_id=case_id,
        event_type=event_type,
        recipient=recipient,
        channel=channel,
        status="Sent"
    )


# ====================================================
# DIGEST / QUEUED NOTIFICATIONS
# ====================================================
def queue_digest_notification(case_id, event_type, recipient, channel, message, link):
    """
    Stores notification for digest delivery
    """

    frappe.get_doc({
        "doctype": "Legal Case Notification Queue",
        "case_id": case_id,
        "event_type": event_type,
        "recipient": recipient,
        "channel": channel,
        "message": message,
        "case_link": link,
        "queued_on": now(),
        "status": "Queued"
    }).insert(ignore_permissions=True)


# ====================================================
# DELIVERY LOGGING (AUDIT)
# ====================================================
def log_notification(case_id, event_type, recipient, channel, status, error=None):
    """
    Stores delivery / failure log
    """

    frappe.get_doc({
        "doctype": "Legal Case Notification",
        "case_id": case_id,
        "event_type": event_type,
        "recipient": recipient,
        "channel": channel,
        "sent_on": now(),
        "delivery_status": status,
        "error_message": error
    }).insert(ignore_permissions=True)


# ====================================================
# HEARING REMINDER SCHEDULER (UC_LEG_009)
# ====================================================
def send_hearing_reminders():
    """
    Runs daily via scheduler
    Sends reminder for hearings scheduled tomorrow
    """

    tomorrow = add_days(nowdate(), 1)

    hearings = frappe.get_all(
        "Legal Case Hearing",
        filters={
            "hearing_date": tomorrow,
            "hearing_status": "Scheduled"
        },
        fields=["name", "case_id", "hearing_date"]
    )

    for h in hearings:
        notify_case_event(
            case_id=h.case_id,
            event_type="Hearing Reminder",
            message=f"Hearing scheduled tomorrow ({h.hearing_date})",
            link=f"{get_url()}/app/legal-case-hearing/{h.name}"
        )
# ====================================================
# COMPLIANCE REMINDER SCHEDULER (UC_LEG_010)
# ====================================================

def send_compliance_reminders():
    tasks = frappe.get_all(
        "Case Compliance Task",
        filters={
            "status": "Pending",
            "reminder_date": nowdate()
        },
        fields=["assigned_to", "case_id", "deadline_date"]
    )

    for t in tasks:
        frappe.sendmail(
            recipients=[t.assigned_to],
            subject="Compliance Deadline Reminder",
            message=f"Compliance task for case {t.case_id} is due on {t.deadline_date}"
        )

def escalate_overdue_tasks():
    tasks = frappe.get_all(
        "Case Compliance Task",
        filters={
            "status": "Pending",
            "deadline_date": ["<", nowdate()]
        }
    )

    for t in tasks:
        doc = frappe.get_doc("Case Compliance Task", t.name)
        doc.status = "Overdue"
        doc.save(ignore_permissions=True)