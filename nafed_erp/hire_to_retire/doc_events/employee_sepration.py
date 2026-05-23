import frappe
from frappe.utils import getdate, nowdate

def validate(doc, method):
    validate_boarding_begins_on(doc)

def validate_boarding_begins_on(doc):
    if doc.boarding_begins_on:
        if getdate(doc.boarding_begins_on) < getdate(nowdate()):
            frappe.throw(
                "Separation Begins  On cannot be a previous date."
            )

# by mayuri
def before_submit(doc, method):
    check_activities_status(doc)

def check_activities_status(doc):
    pending = [r.activity_name for r in doc.activities if r.custom_satus != "Completed"]

    if pending:
        msg = f"<b>Submission Blocked:</b> All activities must be 'Completed'.<br><b>Pending:</b> {', '.join(pending)}"
        frappe.throw(msg, title="Pending Activities")