import frappe
from frappe.utils import add_days, today


def send_due_alerts():

    schedules = frappe.get_all(
        "Fumigation Schedule",
        filters={
            "scheduled_date": add_days(today(), 3),
            "schedule_status": ["!=", "Completed"]
        },
        fields=[
            "name",
            "warehouse",
            "scheduled_date"
        ]
    )

    for doc in schedules:

        frappe.sendmail(
            recipients=["test@example.com"],
            subject="Upcoming Fumigation Alert",
            message=f"""
                Schedule {doc.name}
                is due on {doc.scheduled_date}
            """
        )


def update_overdue_treatments():

    schedules = frappe.get_all(
        "Fumigation Schedule",
        filters={
            "scheduled_date": ["<", today()],
            "schedule_status": ["not in", ["Completed", "Cancelled"]]
        },
        fields=["name"]
    )

    for doc in schedules:

        frappe.db.set_value(
            "Fumigation Schedule",
            doc.name,
            "schedule_status",
            "Overdue"
        )