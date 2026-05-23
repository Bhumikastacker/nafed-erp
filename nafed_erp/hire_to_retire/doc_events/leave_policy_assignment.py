import frappe
from frappe import _
from frappe.utils import getdate

def validate_assignment_dates(doc, method):
    if getdate(doc.effective_from) > getdate(doc.effective_to):
        frappe.throw(_("Effective To date ({0}) cannot be earlier than Effective From date ({1}).")
                         .format(doc.effective_to, doc.effective_from))