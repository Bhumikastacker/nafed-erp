import frappe
from frappe import _
from frappe.utils import getdate

# ==========================================================
# End Date cannot be earlier than Start Date
# ==========================================================

def validate_goal_dates(doc, method):
    if doc.start_date  and doc.end_date:
        if doc.end_date < doc.start_date:
            frappe.throw(
                _("End Date ({0}) cannot be earlier than Start Date ({1}).")
                .format(doc.end_date, doc.start_date)
            )