import frappe
from frappe import _
from frappe.utils import getdate, today

def validate_interview_feedback(doc,method):
    feedback_exists = frappe.db.exists(
        "Interview Feedback",
        {
            "interview": doc.name,
            "docstatus": 1
        }
    )

    if not feedback_exists:
        frappe.throw(
            "Interview Feedback is required before submitting the Interview."
        )



def validate_scheduled_on_date(doc,method):
    if not doc.scheduled_on:
        return

    if getdate(doc.scheduled_on) < getdate(today()):
        frappe.throw(
            "Scheduled On date cannot be before today's date."
        )

# =========================================
# To Time cannot be earlier than From Time
# =========================================

def validate_interview_time(doc, method):
    if doc.from_time and doc.to_time:
        if doc.to_time < doc.from_time:
            frappe.throw(_("To Time cannot be earlier than From Time."))